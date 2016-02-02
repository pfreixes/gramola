# -*- coding: utf-8 -*-
"""
This module implements the helper classes to implement new type of data sources
such as Graphite, CloudWatch, OpenTSDB, etc. The `DataSource` is used as a base
class to implement data sources and the `DataSourceConfig` is used to implement
specific configurations.

:moduleauthor: Pau Freixes, pfreixes@gmail.com
"""

from gramola.utils import (
    InvalidGramolaDictionary,
    GramolaDictionary
)


class InvalidDataSourceConfig(InvalidGramolaDictionary):
    """ Raised when a DataSourceConfig doesn't get the right
    keys. An empty derivated class from InvalidGramolaDictionary just to
    make it readable.
    """
    pass


class OptionalKey(object):
    """ OptionalKey type is used by :class:DataSourceConfig and :class:MetricsQuery
    to store the OPTIONAL_KEYS and helps the gramola commands to build the properly
    arguments.
    """
    def __init__(self, name, description):
        self.name = name
        self.description = description

    def __hash__(self):
        """ OptionalKey instance is hashed over the GramolaDictionary using the name
        of the option"""
        return hash(self.name)

    def __str__(self):
        """ OptionalKeys is get from a dictionary using the name of the option"""
        return self.name

    def __cmp__(self, b):
        """ Compare a OptionKey is just compare the name of the option """
        if type(b) == str:
            return cmp(self.name, b)
        else:
            return super(OptionalKey, self).__cmp__(b)

    @property
    def hyphen_name(self):
        return "--{}".format(self.name)


class DataSourceConfig(GramolaDictionary):
    """ Each data datasource instance is created along with one DataSourceConfig
    that will store the especific keys and values expected to configure one
    data source.

    Each data data source implementation have to implement a derivated of
    DataSourceConfig class configuring the required keys using the
    REQUIRED_KEYS attribute and the optional keys uing the PTIONAL_KEYS
    attribute.

    All DataSourceConfig implementation will have at least the following
    keys: name.
    """
    REQUIRED_KEYS = ('type', 'name',)
    OPTIONAL_KEYS = ()  # tuple of OptionalKey values.

    def __init__(self, *args, **kwargs):
        """
        :raises: InvalidDataSourceConfig
        """
        try:
            super(DataSourceConfig, self).__init__(*args, **kwargs)
        except InvalidGramolaDictionary, e:
            raise InvalidDataSourceConfig(e.errors)


class InvalidMetricQuery(InvalidGramolaDictionary):
    """ Raised when a MetricQuery doesn't get the right
    keys. An empty derivated class from InvalidGramolaDictionary just to
    make it readable.
    """
    pass


class MetricQuery(GramolaDictionary):
    """ Each data datasource implementaiton uses an specific implementation of
    MetricQuery class to get suport for these specific params to make queries
    for an specific datasource.

    Each data data source implementation have to implement a derivated of
    MetricQuery class configuring the required keys using the
    REQUIRED_KEYS and the optional keys uing OPTIONAL_KEYS.

    MetricQuery implements the following keys : metric.
    """
    REQUIRED_KEYS = ('metric',)
    OPTIONAL_KEYS = ()  # tuple of OptionalKey values.

    def __init__(self, *args, **kwargs):
        """
        :raises: InvalidMetricQuery
        """
        try:
            super(MetricQuery, self).__init__(*args, **kwargs)
        except InvalidGramolaDictionary, e:
            raise InvalidMetricQuery(e.errors)


class DataSource(object):
    """ Used as a base class for specialized data sources such as
    Graphite, OpenTSDB, and others.

    Those methods that raise a NotImplemented exception have to be
    defined by the derivated class.
    """

    # Override these class attributes with the specific
    # implementation by the type of data source.
    DATA_SOURCE_CONFIGURATION_CLS = DataSourceConfig
    METRIC_QUERY_CLS = MetricQuery

    # Override the TYPE attribute with the short name
    # of the DataSource.
    TYPE = None

    @classmethod
    def find(cls, type_):
        """Returns the DataSource implementation for a specific type_."""
        try:
            return next(c for c in cls.__subclasses__() if c.TYPE == type_)
        except StopIteration:
            raise KeyError(type_)

    @classmethod
    def implementations(cls):
        """Returns all implementations."""
        return cls.__subclasses__()

    def __init__(self, configuration):
        """
        Initialize a data source using a configuration. Configuration is, if it
        is not override, a instance of the
        DataSource.DATA_SOURCE_CONFIGURATION_CLS configuration class.

        :param configuration: Data Source configuration
        :type configuration: `DataSourceConfig` or a derivated one
        """
        self.configuration = configuration

    @classmethod
    def from_config(cls, **config_params):
        """ Build a datasource using the config_params given """
        return cls(cls.DATA_SOURCE_CONFIGURATION_CLS(**config_params))

    def suggestions(self, current, key='name'):
        """
        Function used to get a list of suggested values by the data source to
        complete the `current` value.

        Key by default looks at the `name` query param and is called when the user
        runs the following command and gets an autocompletion :

            $ gramola query datasource metric.path...

        But if the data source implements other keys using a specific MetricQuery
        derivated class the suggestion can come fromm an specific command option
        that looks at this value, for example

            $ gramola query datasource metric.path.value --since=

        In the previous example the `key` param will get `since` as a value.

        By default if it is not implemented it returns a empty list of values.

        :param current: Current path value.
        :type current: string.
        :param key: The param over we have to make the suggestion, defaults as `name`
        :type key: string.
        :rtype: list.
        """
        return []

    def datapoints(self, query, maxdatapoints=None):
        """ This function is used to pick up a set of datapoints
        from the data source configured.

        The `query` object holds the query params given by the user, is
        a instance, if if is not override, of the `DataSource.METRIC_QUERY_CLS`

        :param configuration: Query
        :type configuration: `MetricQuery` or a derivated one
        :param maxdatapoints: Restrict the result with a certain amount of datapoints, default All
        :rtype: list, or None when where datapoints were not found.
        """
        raise NotImplemented()

    def test(self):
        """ This function is used to test a data source configuration.

        Derivated class has to implement this function if its wants to
        give support for testing a datasource configuration used by
        the commands `gramola datasource-add` and  `gramola datasource-test`
        :rtype: boolean.
        """
        raise NotImplemented()
