import pytest

from json import loads
from copy import copy

from gramola.commands import (
    GramolaCommand,
    DataSourceEchoCommand
)

from gramola.datasources.base import (
    MetricQuery,
    DataSource,
    DataSourceConfig
)

@pytest.fixture
def test_data_source():
    class TestDataSourceConfig(DataSourceConfig):
        REQUIRED_KEYS = ('foo', 'bar')
        OPTINOAL_KEYS = ('gramola',)

    class TestMetricQuery(MetricQuery):
        REQUIRED_KEYS = ('since', 'until')

    class TestDataSource(DataSource):
        TYPE = 'test'
        DATA_SOURCE_CONFIGURATION_CLS = TestDataSourceConfig
        METRIC_QUERY_CLS = TestMetricQuery

class TestGramolaCommand(object):
    def test_interface(self):
        class TestCommand(GramolaCommand):
            NAME = 'test'
        assert GramolaCommand.find('test') == TestCommand
        with pytest.raises(KeyError):
            GramolaCommand.find('foo')

class TestDataSourceEcho(object):
    def test_execute(self, test_data_source):
        d = {'type': 'test', 'foo': 1, 'bar': 1}

        # otupus returns a hardcoed name
        output = copy(d)
        output.update(name='stdout')

        assert loads(DataSourceEchoCommand.execute(
            **d)) == output
