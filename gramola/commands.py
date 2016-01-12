# -*- coding: utf-8 -*-
"""
Commands are called from the entry point generated by the setuptools. The set
of commands supported are:

  * gramola types                  : List of the datasource types supported.
  * gramola datasource             : Show a specific datasource.
  * gramola datasource-test        : Test a specific datasource.
  * gramola datasource-list        : List all datasources.
  * gramola datasource-rm          : Remove one datasource.
  * gramola datasource-add-<type>  : Add a new datasource.
  * gramola datasource-echo-<type> : Echo a datasource.
  * gramola query-<type>           : Run a metrics query.
  * gramola dashboard              : Show a specific dashboard.
  * gramola dashboard-list         : List all dashboards.
  * gramola dashboard-rm           : Remove a dashboard.
  * gramola dashboard-rm-query     : Remove a specific query from one dashboard.
  * gramola dashboard-query        : Run all dashboard metrics.

:moduleauthor: Pau Freixes, pfreixes@gmail.com
"""
from __future__ import print_function

import sys
import optparse
import sparkline

from json import loads

from gramola import log
from gramola.contrib.subcommand import (
    Subcommand,
    SubcommandsOptionParser
)
from gramola.datasources.base import (
    DataSource,
    InvalidMetricQuery,
    InvalidDataSourceConfig
)


class InvalidParams(Exception):
    def __init__(self, error_params):
        self.error_params = error_params
        Exception.__init__(self)


class GramolaCommand(object):
    # to be overriden by commands implementations
    NAME = None
    DESCRIPTION = None
    USAGE = None

    @staticmethod
    def execute(*args, **kwargs):
        raise NotImplemented()

    @staticmethod
    def options():
        """List of option args and kwargs to be used as a params for the
        parser.add_option function."""
        return []

    @classmethod
    def find(cls, command_name):
        """Returns the Command implementation for a specific command name."""
        try:
            return next(c for c in cls.__subclasses__() if c.NAME == command_name)
        except StopIteration:
            raise KeyError(command_name)

    @classmethod
    def commands(cls):
        """Returns the commands implementations"""
        return cls.__subclasses__()


class DataSourceCommand(GramolaCommand):
    NAME = 'datasource'
    DESCRIPTION = 'View the details of a saved datasource'
    USAGE = '%prog NAME'

    @staticmethod
    def execute(name, store=None):
        """ Returns info about one specific datasource as a dictionary with all
        key values saved. For Example:

            {
                "name": "datasource name",
                "type": "graphite",
                "url": "http://localhost:9000"
            }

        :param name: Name of the datasource.
        :param store: Alternatvie :class:`gramola.store.Store` to the default one.
        :rtype: dict.
        :raises KeyError: If the given datasource name does not exist.
        """
        user_store = store or DefaultStore()

        try:
            return filter(lambda d: d['name'] == name, user_store.datasources())[0]
        except IndexError:
            raise KeyError(name)


def datasource_test(name, store=None):
    """ Test an already saved datasource.

    :param name: Name of the datasource.
    :param store: Alternatvie :class:`gramola.store.Store` to the default one.
    :raises gramola.datasource.DataSourceNotFound: If the given name does not exist.
    """
    raise NotImplemented()


def datasource_rm(name, store=None):
    """ Removes an already saved datasource.

    :param name: Name of the datasource.
    :param store: Alternatvie :class:`gramola.store.Store` to the default one.
    :rtype: boolean.
    :raises gramola.datasource.DataSourceNotFound: If the given name does not exist.
    """
    raise NotImplemented()


def datasource_add(name, store=None, dry_mode=False, test=True, **datasource_params):
    """ Add a new datasource with a specific `name`. The params of the datasource depends
    of the type of data source.

    :param name: Name of the datasource.
    :param store: Alternatvie :class:`gramola.store.Store` to the default one.
    :param dry_mode: Dont save at last, usefull combined with `test` enabled to check
                     that the datasource works.
    :param datasource_params: Specific keyword arguments for the datasource.
    :rtype: boolean.
    :raises KeyError: If the type of data source is not implemented.
    :raises gramola.datasource.InvalidDataSourceConfig: The datasource_params are invalid.
    :raises gramola.store.DuplicateEntry: If the datasource name already exists.
    """
    # find the right class ipmlementation
    cls_datasource = DataSources.find([datasource_params['type']])

    # create a spceific configuration for this data source and instantiate
    config = cls_datasource.DATA_SOURCE_CONFIGURATION_CLS(**datasource_params)
    data_source = cls_datasource(config)

    # if test is not disabled specifically the datasource wont be saved
    # until it will pass the test step.
    if test:
        try:
            if not data_source.test():
                log.error("Testing the datasource .... Failed")
                return False
            log.info("Testing the datasource .... Ok")
        except Exception, e:
            log.error("Testing the datasource .... Error")
            raise e

    if dry_mode:
        log.info("Running in dry-mode, nothing more todo")
        return True

    user_store = store or DefaultStore()
    user_store.save_datasource(config)


def build_datasource_echo_type(datasource):
    """
    Build the datasource-echo command for one type of datasource, it turns out
    in a new command named as datasource-echo-<type>.
    """
    class DataSourceEchoCommand(GramolaCommand):
        NAME = 'datasource-echo-{}'.format(datasource.TYPE)
        DESCRIPTION = 'Echo a datasource {} configuration'.format(datasource.TYPE)

        # All datasources inherited the `type` and the `name` fields as a
        # required params, typed commands have already the type and they are
        # removed as command args. And in the Echo case also the name.
        USAGE = '%prog {}'.format(" ".join(
            [s.upper() for s in datasource.DATA_SOURCE_CONFIGURATION_CLS.required_keys() if
                s not in ['name', 'type']]))

        @staticmethod
        def execute(options, *datasource_args):
            """ Echo a datasource configuration to be used by query command, the arguments
            depend on the kind of datasource.

            :param options: Options given along with the command arguments. Use it to find out
                            specific options for the data source.
            :param datasource_args: Values of the required keys for the datasource.
            :return: A valid payload to be used as stdin of the query-<type> command.
            :raises InvalidParams: If datasource_args are not completed.
            """
            datasource_params = {
                # Type is a required param that is coupled with
                # with the command.
                'type': datasource.TYPE,

                # A echo command doesnt need the name keyword even it is required,
                # we share the same interface than the command to add datasources then
                # we have to give a automatic name to avoid raise an
                # InvalidDataSourceConfig error
                'name': 'stdout'
            }

            datasource_params.update(
                {k: v for v, k in
                    zip(datasource_args,
                        filter(lambda k: k not in ['name', 'type'],
                               datasource.DATA_SOURCE_CONFIGURATION_CLS.required_keys()))}
            )

            try:
                print(datasource.DATA_SOURCE_CONFIGURATION_CLS(
                        **datasource_params).dumps())
            except InvalidDataSourceConfig, e:
                raise InvalidParams(e.errors)

        @staticmethod
        def options():
            return [(None, "--{}".format(key), key) for key in
                    datasource.DATA_SOURCE_CONFIGURATION_CLS.optional_keys()]

    return DataSourceEchoCommand


class DataSourceListCommand(GramolaCommand):
    NAME = 'datasource-list'
    DESCRIPTION = 'List all saved datasources'

    @staticmethod
    def execute(store=None):
        """ List all datasouces.

        :param store: Alternatvie :class:`gramola.store.Store` to the default one.
        :return: list of derivated instancess of
                 :class:`gramola.datasources.base.DataSourceConfig`
        """
        user_store = store or DefaultStore()
        return user_store.datasources()


def build_datasource_query_type(datasource):
    """
    Build the query command for one type of datasource, it turns out
    in a new command named as query-<type>.
    """

    class QueryCommand(GramolaCommand):
        NAME = 'query-{}'.format(datasource.TYPE)
        DESCRIPTION = 'Query for a specific metric.'
        USAGE = '%prog {}'.format(" ".join(
            ['DATASOURCE_NAME'] +
            [s.upper() for s in datasource.METRIC_QUERY_CLS.required_keys()]))

        @staticmethod
        def execute(options, datasource_name, *query_args):
            """ Runs a query using a datasource and print it as a char graphic

            :param options: Options given along with the command arguments. Use it to find out
                            specific options for the query args.
            :param datasource_name: Name of the datasource used, the datasource will be get from
                                    the user store. Altought special char `-` can be used as
                                    alternative to read the datasource config from the stdin.
            :param query_args: Arguments given as metrics query, specific for each metric query.
            :raises InvalidDataSourceConfig: Data source config is invalid.
            :raises InvalidMetricQuery: Query params are invalid.
            :raises ValueError: If the given datasource from stdin is not well formatted.
            """
            if datasource_name == '-':
                buffer_ = sys.stdin.read()
                config = loads(buffer_)
            else:
                user_store = store or DefaultStore()
                try:
                    config = filter(lambda d: d['name'] == datasource_name,
                                    user_store.datasources())[0]
                except IndexError:
                    print("Datasource {} not found".format(datasource_name), file=sys.stderr)
                    return

            query_params = {
                k: v for v, k in zip(query_args,
                                     datasource.METRIC_QUERY_CLS.required_keys())
            }

            # set also the optional keys given as optional params
            query_params.update(**{str(k): getattr(options, str(k))
                                for k in filter(lambda k: getattr(options, str(k)),
                                datasource.METRIC_QUERY_CLS.optional_keys())})

            try:
                query = datasource.METRIC_QUERY_CLS(**query_params)
            except InvalidMetricQuery, e:
                raise InvalidParams(e.errors)

            try:
                datapoints = datasource.from_config(**config).datapoints(query)
                if datapoints:
                    print(sparkline.sparkify([value for value, ts in datapoints]))
            except InvalidDataSourceConfig, e:
                print("Datasource config invalid {}".format(e.errors), file=sys.stderr)

        @staticmethod
        def options():
            # Command Options
            command_options = []

            # Datasource Options
            datasource_options = [
                ((option.hyphen_name,), {"dest": option.name, "help": option.description})
                for option in datasource.METRIC_QUERY_CLS.optional_keys()]

            return command_options + datasource_options

    return QueryCommand


def gramola():
    """ Entry point called from binary generated by setuptools. Beyond
    the main command Gramola immplements a sub set of commands that each one
    implements an specific opeartion. The anatomy of a Gramola command looks like:

        $ gramola <global options> <subcommand> <subcommand options> <args ..>
    """
    # Build as many datasource-echo commands as many types of datasources there are.
    typed_commands = [build_datasource_echo_type(datasource)
                      for datasource in DataSource.implementations()]

    # Build as many query commands as many types of datasources there are.
    query_commands = [build_datasource_query_type(datasource)
                      for datasource in DataSource.implementations()]

    # Use the gramola.contrib.subcommands implementation to wraper the
    # GramolaCommands as a subcommands availables from the main command.
    subcommands = []
    for gramola_subcommand in GramolaCommand.commands():
        cmd = Subcommand(gramola_subcommand.NAME,
                         optparse.OptionParser(usage=gramola_subcommand.USAGE),
                         gramola_subcommand.DESCRIPTION)
        for option_args, option_kwargs in gramola_subcommand.options():
            cmd.parser.add_option(*option_args, **option_kwargs)

        subcommands.append(cmd)

    parser = SubcommandsOptionParser(subcommands=subcommands)
    parser.add_option('-s', '--store', dest='store',
                      help='alternative store directory, default ~/.gramola')
    parser.add_option('-q', dest='quite', help='Be quite', action='store_true')
    parser.add_option('-v', dest='verbose', help='Be verbose', action='store_true')

    options, subcommand, suboptions, subargs = parser.parse_args()
    log.setup(verbose=options.verbose, quite=options.quite)
    try:
        cmd = GramolaCommand.find(subcommand.name)
    except KeyError:
        print("Command not found {}".format(subcommand.name))
        print("")
        parser.print_help()
        sys.exit(1)

    try:
        cmd.execute(suboptions, *subargs)
    except InvalidParams, e:
        print("{} invalid params {}".format(subcommand.name, e.error_params))
        sys.exit(1)
