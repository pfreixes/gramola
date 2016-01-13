import pytest

from mock import Mock

from gramola.store import Store
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


CONFIG = """
[datasource one]
type=test
foo=a
bar=b

[datasource two]
type=test
foo=c
bar=d
gramola=e
"""


@pytest.fixture
def nonedefault_store(tmpdir):
    fd = tmpdir.join(Store.DEFAULT_DATASOURCES_FILENAME)
    fd.write(CONFIG)
    return Store(path=str(tmpdir))
