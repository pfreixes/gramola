import pytest

from gramola.datasources.base import (
    DataSource,
    DataSourceConfig,
    InvalidDataSourceConfig,
    MetricQuery,
    InvalidMetricQuery
)

class TestDataSourceConfig(object):

    def test_interface(self):
        class TestConfig(DataSourceConfig):
            REQUIRED_KEYS = ('foo',)

        conf = TestConfig(**{'type': 'test', 'name': 'datasource', 'foo': 1})
        assert conf.type == 'test'
        assert conf.name == 'datasource'
        assert conf.foo == 1

    def test_custom_raises(self):
        class TestConfig(DataSourceConfig):
            pass

        # requires the name key
        with pytest.raises(InvalidDataSourceConfig):
            TestConfig(**{})


class TestMetricQuery(object):

    def test_interface(self):
        class TestQuery(MetricQuery):
            REQUIRED_KEYS = ('from_', 'to')

        query = TestQuery(**{'metric': 'cpu', 'from_': 1 , 'to': 2})
        assert query.metric == 'cpu'
        assert query.from_ == 1
        assert query.to == 2

    def test_custom_raises(self):
        class TestQuery(MetricQuery):
            pass

        # requires the metric key
        with pytest.raises(InvalidMetricQuery):
            TestQuery(**{})


class TestDataSource(object):

    def test_find(self):
        class TestDataSource(DataSource):
            TYPE = 'test'

        assert DataSource.find('test') == TestDataSource

        with pytest.raises(KeyError):
            DataSource.find('foo')