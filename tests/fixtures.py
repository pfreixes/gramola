import pytest

from mock import Mock

from gramola.datasources.base import (
    MetricQuery,
    DataSource,
    DataSourceConfig
)

@pytest.fixture
def test_data_source():
    class TestDataSourceConfig(DataSourceConfig):
        REQUIRED_KEYS = ('foo', 'bar')
        OPTIONAL_KEYS = ('gramola',)

    class TestMetricQuery(MetricQuery):
        REQUIRED_KEYS = ('since', 'until')

    class TestDataSource(DataSource):
        TYPE = 'test'
        DATA_SOURCE_CONFIGURATION_CLS = TestDataSourceConfig
        METRIC_QUERY_CLS = TestMetricQuery

        datapoints = Mock()

    return TestDataSource
