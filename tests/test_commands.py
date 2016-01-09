import pytest
import sparkline

from copy import copy
from json import loads, dumps
from mock import patch, Mock

from gramola.commands import (
    InvalidParams,
    GramolaCommand,
    build_datasource_echo_type,
    build_datasource_query_type
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

        datapoints = Mock()

    return TestDataSource

class TestGramolaCommand(object):
    def test_interface(self):
        class TestCommand(GramolaCommand):
            NAME = 'test'
        assert GramolaCommand.find('test') == TestCommand
        with pytest.raises(KeyError):
            GramolaCommand.find('foo')

        assert TestCommand in GramolaCommand.commands() 

class TestDataSourceEcho(object):
    def test_execute(self, test_data_source):
        # otupus returns a hardcoded name and the type of the
        # datasource along with the expected keys of datasource
        output = {
            'type': 'test',
            'name': 'stdout',
            'bar': 2,
            'foo': 1,
        }
        command = build_datasource_echo_type(test_data_source)
        with patch("__builtin__.print") as print_patched:
            command.execute(1, 2)
            print_patched.assert_called_with(dumps(output))

    def test_invalid_params(self, test_data_source):
        # test_data_source takes two params
        command = build_datasource_echo_type(test_data_source)
        with pytest.raises(InvalidParams):
            command.execute(1)


class TestQueryCommand(object):
    @patch("gramola.commands.sys")
    def test_execute_stdin(self, sys_patched, test_data_source):
        buffer_ = dumps({'type': 'test', 'name': 'stdout', 'foo': 1, 'bar': 1})
        sys_patched.stdin.read.return_value = buffer_

        test_data_source.datapoints.return_value = [(1, 0), (2, 1), (3, 1)]

        command = build_datasource_query_type(test_data_source)
        with patch("__builtin__.print") as print_patched:
            command.execute("-", "foo", "-1d", "now")
            print_patched.assert_called_with(sparkline.sparkify([1, 2, 3]))

        test_data_source.datapoints.assert_call_with(
            test_data_source.METRIC_QUERY_CLS(metric='foo', since='-1d', until='now')
        )

    @patch("gramola.commands.sys")
    def test_invalid_params(self, sys_patched, test_data_source):
        # query test_data_source takes four required params 
        buffer_ = dumps({'type': 'test', 'name': 'stdout', 'foo': 1, 'bar': 1})
        sys_patched.stdin.read.return_value = buffer_
        command = build_datasource_echo_type(test_data_source)
        with pytest.raises(InvalidParams):
            command.execute("-")


