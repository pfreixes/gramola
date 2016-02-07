# -*- coding: utf-8 -*-
"""
Utils used arround the Gramola project.

:moduleauthor: Pau Freixes, pfreixes@gmail.com
"""
import json

from itertools import chain
from datetime import datetime
from datetime import timedelta


class InvalidGramolaDictionary(Exception):
    """ Exception raised when the keys given to one GramolaDictionary instance
    or a derivated instance class doesn't give all the needed keys.
    """
    def __init__(self, errors):
        """
        :paramm errors: a dictionary with the keys and their errors.
        :type errors: dict.
        """
        Exception.__init__(self)
        self.errors = errors


class GramolaDictionary(object):
    """
    Implements a dictionary store with a interface to declare the allowable
    keys, either required or optional.

    Each derivated implementation of GramolaDictionary can configure the
    required keys using the REQUIRED_KEYS attribute and the optional keys
    using OPTIONAL_KEYS attribute. These params will be concatenated with
    the params defined by the base class.

    As the required keys and the optional keys are automatically published
    as properties, for these optional keys that are not given a None value
    is returned.

    For example:

        >>> class Config(GramolaDictionary):
        >>>     REQUIRED_KEYS = (name,)
        >>>
        >>> class MyConfig(Config):
        >>>     REQUIRED_KEYS = (foo,)
        >>>     OPTIONAL_KEYS = (bar,)
        >>>
        >>> conf = MyConfig({'name':'hellow', 'foo': 'x'})
        >>> conf.name
        hellow
        >>> conf.foo
        x
        >>> conf.bar
        None

    The name of the keys then have to follow the naming convention for Python
    class attributes.
    """
    REQUIRED_KEYS = ()
    OPTIONAL_KEYS = ()

    # Use a metaclass to publish dynamic properties
    # got from the REQUIRED_KEYS and OPTIONAL_KEYS published
    # by the base classes + derivated class
    class __metaclass__(type):
        def __init__(cls, name, bases, nmspc):
            type.__init__(cls, name, bases, nmspc)

            # install the property for all keys to make them visible
            # as a properties. i.e conf.name
            for attr in chain(cls.required_keys(), cls.optional_keys()):
                setattr(
                    cls,
                    str(attr),  # required for non string objects
                    property(lambda self, a=attr: self._dict.get(a, None))
                )

    def __init__(self, **kwargs):
        """
        Initialize a GramolaDictionary instance.

        :param kwargs: key, value pairs used for this configuration.
        :type kwargs: dict.
        :raises : InvalidDataSourceConfig.
        """
        # check that the keys given as a confiugaration keys are allowed either because
        # are required or optional.
        allowed_keys = self.required_keys() + self.optional_keys()
        if filter(lambda k: k not in allowed_keys, kwargs):
            raise InvalidGramolaDictionary(
                {k: 'Key not expected' for k in
                    filter(lambda k: k not in allowed_keys, kwargs)})

        # all required keys have to be given
        if filter(lambda k: k not in kwargs, self.required_keys()):
            raise InvalidGramolaDictionary(
                {k: 'Key missing' for k in
                    filter(lambda k: k not in kwargs, self.required_keys())})

        self._dict = kwargs

    def __eq__(self, b):
        # Are equals if they are implemented using the same class and
        # have the same dictionary elements
        return self.__class__ == b.__class__ and self._dict == b._dict

    def dict(self):
        """ Returns a copy dict of the internal dict"""
        return dict(**self._dict)

    def dumps(self):
        """ Return a string JSON object to be used as a serialized """
        return json.dumps(self._dict)

    @classmethod
    def loads(cls, buffer_):
        """ Return a instancia of cls using the JSON buffer_ as a kwargs
        for the constructor.

        :param buffer_: str.
        """
        return cls(**json.loads(buffer_))

    @classmethod
    def required_keys(cls):
        """ Return all required keys inherited by the whole hierarchy classes """
        return cls._pick_up_attr('REQUIRED_KEYS')

    @classmethod
    def optional_keys(cls):
        """ Return all optional keys inherited by the whole hierarchy classes """
        return cls._pick_up_attr('OPTIONAL_KEYS')

    @classmethod
    def _pick_up_attr(cls, attr):
        values = getattr(cls, attr)
        for base in cls.__bases__:
            if hasattr(base, '_pick_up_attr'):
                values += base._pick_up_attr(attr)

        # the values are picked up from top to button, they
        # have to seen inside out, lets return from button
        # to top
        return tuple(v for v in reversed(values))


class DateTimeInvalidValue(Exception):
    pass


def parse_date(date_value):
    """ Parse a date_value expecting at least one of the following
    formats, otherwise it raises a DateTimeInvalidValue.

        timestamp format: 1454867898
        iso8601 format  : 2016-02-06T20:37:47
        human format    : -1h, -5min, 10d, now, ...
                          ([|-](integer)[h|min|s|d]|now)

    :param date_value: str
    :return: datetime
    """
    try:
        return datetime.strptime(date_value, "%Y-%m-%dT%H:%M:%S")
    except ValueError:
        try:
            return datetime.fromtimestamp(float(date_value))
        except ValueError:
            try:
                if date_value == 'now':
                    return datetime.now()
                elif date_value.find("h") != -1:
                    v = date_value.split("h")[0]
                    if v[0] == '-':
                        return datetime.now() - timedelta(hours=int(v[1:]))
                    else:
                        return datetime.now() + timedelta(hours=int(v))
                elif date_value.find("min") != -1:
                    v = date_value.split("min")[0]
                    if v[0] == '-':
                        return datetime.now() - timedelta(minutes=int(v[1:]))
                    else:
                        return datetime.now() + timedelta(minutes=int(v))
                elif date_value.find("s") != -1:
                    v = date_value.split("s")[0]
                    if v[0] == '-':
                        return datetime.now() - timedelta(seconds=int(v[1:]))
                    else:
                        return datetime.now() + timedelta(seconds=int(v))
                elif date_value.find("d") != -1:
                    v = date_value.split("d")[0]
                    if v[0] == '-':
                        return datetime.now() - timedelta(days=int(v[1:]))
                    else:
                        return datetime.now() + timedelta(days=int(v))
                raise DateTimeInvalidValue()
            except ValueError:
                raise DateTimeInvalidValue()
    return data_value
