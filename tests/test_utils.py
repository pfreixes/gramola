import pytest
import json
import time

from datetime import datetime
from datetime import timedelta

from gramola.utils import (
    parse_date,
    DateTimeInvalidValue,
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
        assert not conf.banana
        assert not conf.gramola
        assert conf.dumps() == json.dumps({'name': 'hellow', 'foo': 1, 'bar': 2})
        assert ChildConfig.optional_keys() == ('banana', 'gramola', 'bar')
        assert ChildConfig.required_keys() == ('name', 'foo')

        ChildConfig.loads(json.dumps({'name': 'hellow', 'foo': 1, 'bar': 2}))

        # check the __eq__ method
        conf2 = ChildConfig(**{'name': 'hellow', 'foo': 1, 'bar': 2})
        assert conf == conf2

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


class TestParseDate(object):
    def test_now(self):
        dt = datetime.now()
        # skip milisecons
        assert parse_date('now').timetuple()[:-1] == dt.timetuple()[:-1]

    def test_1min(self):
        dt = datetime.now() - timedelta(minutes=1)
        assert parse_date('-1min').minute == dt.minute

    def test_1s(self):
        dt = datetime.now() - timedelta(seconds=1)
        assert parse_date('-1s').second == dt.second

    def test_1h(self):
        dt = datetime.now() - timedelta(hours=1)
        assert parse_date('-1h').hour == dt.hour

    def test_1d(self):
        dt = datetime.now() - timedelta(days=1)
        assert parse_date('-1d').day == dt.day

    def test_timestamp(self):
        dt = datetime.now()
        assert parse_date(str(round(time.mktime(dt.timetuple()), 0))).timetuple()[:-1] ==\
            dt.timetuple()[:-1]

    def test_iso8601(self):
        dt = datetime.now()
        assert parse_date(dt.strftime("%Y-%m-%dT%H:%M:%S")).timetuple()[:-1] ==\
            dt.timetuple()[:-1]

    def test_invalid(self):
        with pytest.raises(DateTimeInvalidValue):
            parse_date("asdfasdfasdf")
