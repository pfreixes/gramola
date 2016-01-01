import pytest
import json

from gramola.utils import (
    GramolaDictionary,
    InvalidGramolaDictionary
)

class TestGramolaDictionary(object):

    def test_interface(self):
        class ParentConfig(GramolaDictionary):
            REQUIRED_KEYS = ('name',)
            OPTIONAL_KEYS = ('banana',)

        class ChildConfig(ParentConfig):
            REQUIRED_KEYS = ('foo',)
            OPTIONAL_KEYS = ('bar', 'gramola')

        conf = ChildConfig(**{'name': 'hellow', 'foo': 1, 'bar': 2})
        assert conf.name == 'hellow'
        assert conf.foo == 1
        assert conf.bar == 2
        assert conf.banana == None
        assert conf.gramola == None
        assert conf.dumps() == json.dumps({'name': 'hellow', 'foo': 1, 'bar': 2})
        assert ChildConfig.optional_keys() == ('bar', 'gramola', 'banana')
        assert ChildConfig.required_keys() == ('foo', 'name')

        ChildConfig.loads(json.dumps({'name': 'hellow', 'foo': 1, 'bar': 2}))

    def test_allowed_keys(self):
        class TestConfig(GramolaDictionary):
            REQUIRED_KEYS = ('foo',)
            OPTIONAL_KEYS = ('bar', 'gramola')

        # requires the foo key
        with pytest.raises(InvalidGramolaDictionary):
            TestConfig(**{})

        # invalid key given
        with pytest.raises(InvalidGramolaDictionary):
            TestConfig(**{'foo': 1, 'whatever': None})

        with pytest.raises(InvalidGramolaDictionary):
            TestConfig(**{'bar': None})
