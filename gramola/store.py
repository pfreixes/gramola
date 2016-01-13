# -*- coding: utf-8 -*-
"""
This module implements the Store interface to save dashboards and datasources
to use them after. By default Gramola uses the directory ~/.gramola, although
all Gramola commands can override this default path for another one.

:moduleauthor: Pau Freixes, pfreixes@gmail.com
"""
import os

from configobj import ConfigObj

from gramola import log
from gramola.datasources.base import DataSource


class NotFound(Exception):
    pass


class DuplicateEntry(Exception):
    pass


class Store(object):
    DEFAULT_DIRNAME = ".gramola"
    DEFAULT_DASHBOARDS_FILENAME = "dashboards"
    DEFAULT_DATASOURCES_FILENAME = "datasources"

    def __init__(self, path=None):
        """
        Initialize a Store instane looking into the default store path or an
        alternavite given by the `path` keyword.

        :param path: string, an alternative path to the default one
        """
        if not path:
            # Use the default one, in that case first time we create it
            path = os.path.join(os.path.expanduser("~"), Store.DEFAULT_DIRNAME)
            if not os.path.exists(path):
                os.makedirs(path)

            self.path = path
        else:
            # Custom paths have to be checked
            if not os.path.exists(path):
                raise ValueError("Path {} does not exists".format(path))
            self.path = path

        self.dashboards_filepath = os.path.join(self.path, Store.DEFAULT_DASHBOARDS_FILENAME)
        self.datasources_filepath = os.path.join(self.path, Store.DEFAULT_DATASOURCES_FILENAME)

    def datasources(self, name=None, type_=None):
        """
        Return all datasources stored as a list of dictionaries, each dictionary
        is instance of :class:gramola.datasources.base.DataSourceConfig or derivated
        one representing the data source by it self.

        Use the keywords `name` and `type_` to filter datasources for one or both
        fields.

        :param name: string, filter by name.
        :param type_: string, filter by type_ of datasource.
        :return: list
        """
        config = ConfigObj(self.datasources_filepath, create_empty=True)
        results = []
        for section in config.sections:
            # User filters
            if name and name != section:
                continue

            if type_ and type_ != config[section].get('type'):
                continue

            # The title of the section is the name of the data source, we have to
            # pack it by hand. Each section as at least the type key used to find out
            # the right DataSourceConfig derivated class.
            factory = DataSource.find(config[section].get('type')).DATA_SOURCE_CONFIGURATION_CLS
            keys = {k: v for k, v in config[section].items()}
            keys.update({'name': section})
            results.append(factory(**keys))

        return results

    def add_datasource(self, datasource):
        """
        Store a datasource to the system.

        :param datasource: :class:gramola.datasources.base.DatSourceConfig.
        :raises gramola.store.DuplicateEntry: If the datasource name already exists.
        """
        config = ConfigObj(infile=self.datasources_filepath, create_empty=True)
        if datasource.name in config:
            raise DuplicateEntry()

        config[datasource.name] = datasource.dict()
        config.write()

    def rm_datasource(self, name):
        """
        Remove a datasource from the system.

        :param name: string, name of the data source to remove.
        :raises gramola.store.NotFound: If the datasource does not exists.
        """
        config = ConfigObj(infile=self.datasources_filepath, create_empty=True)
        if name not in config:
            raise NotFound()

        config.pop(name)
        config.write()

    def dashboards(self, name=None):
        """
        Return all datshboards stored as a list of dictionaries, each dictionary
        has the name of the dashbaord and the metrics queries related with its.
        For 

            [{"name": "dashboard name", "queries": [{query1}, {query2} ..... ]]

        Each query is a dictionary formed by the name of the datasource that the
        query uses and the required keys and the optional keys of each kind of metric
        query. For example:

            { "dastasource_name": "datasource name", ... metrics query fields ..}

        :param name: string, filter by name.
        :return: list
        """
        raise NotImplemented()
