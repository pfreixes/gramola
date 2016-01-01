# -*- coding: utf-8 -*-
"""
Utils used arround the Gramola project.

:moduleauthor: Pau Freixes, pfreixes@gmail.com
"""
import json

from itertools import chain

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
                    attr,
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
                {k:'Key not expected' for k in
                    filter(lambda k: k not in allowed_keys, kwargs)})

        
        # all required keys have to be given
        if filter(lambda k: k not in kwargs, self.required_keys()):
            raise InvalidGramolaDictionary(
                {k:'Key missing' for k in
                    filter(lambda k: k not in kwargs, self.required_keys())})

        self._dict = kwargs

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
        return values