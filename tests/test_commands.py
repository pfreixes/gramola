import pytest
import sparkline

from copy import copy
from json import loads, dumps
from mock import patch, Mock

from gramola.commands import (
    InvalidParams,
    GramolaCommand,
    DataSourceCommand,
    DataSourceRmCommand,
    DataSourceTestCommand,
    DataSourceListCommand,
    build_datasource_add_type,
    build_datasource_echo_type,
    build_datasource_query_type
)

from gramola.datasources.base import (
    MetricQuery,
    DataSource,
    DataSourceConfig
)

from .fixtures import test_data_source
from .fixtures import nonedefault_store


@pytest.fixture
def empty_options(nonedefault_store):
    return Mock()


@pytest.fixture
def empty_suboptions():
    return Mock()


class TestGramolaCommand(object):
    def test_interface(self):
        class TestCommand(GramolaCommand):
            NAME = 'test'
        assert GramolaCommand.find('test') == TestCommand
        with pytest.raises(KeyError):
            GramolaCommand.find('foo')

        assert TestCommand in GramolaCommand.commands()


class TestDataSource(object):
    def test_execute(self, empty_options, empty_suboptions, test_data_source, nonedefault_store):
        empty_options.store = nonedefault_store.path
        output = {
            'type': 'test',
            'name': 'datasource one',
            'bar': 'b',
            'foo': 'a'
        }
        with patch("__builtin__.print") as print_patched:
            DataSourceCommand.execute(empty_options, empty_suboptions, "datasource one")
            print_patched.assert_called_with(dumps(output))

    def test_execute_not_found(self, empty_options, empty_suboptions,
                               test_data_source, nonedefault_store):
        empty_options.store = nonedefault_store.path
        with patch("__builtin__.print") as print_patched:
            DataSourceCommand.execute(empty_options, empty_suboptions, "xxxx")
            print_patched.assert_called_with("Datasource `xxxx` NOT FOUND")

    def test_invalid_params(self, empty_options, empty_suboptions,
                            test_data_source, nonedefault_store):
        empty_options.store = nonedefault_store.path
        # DataSource takes one param
        with pytest.raises(InvalidParams):
            DataSourceCommand.execute(empty_options, empty_suboptions)


class TestDataSourceRm(object):
    def test_execute(self, empty_options, empty_suboptions, test_data_source, nonedefault_store):
        empty_options.store = nonedefault_store.path
        with patch("__builtin__.print") as print_patched:
            DataSourceRmCommand.execute(empty_options, empty_suboptions, "datasource one")
            print_patched.assert_called_with("Datasource `datasource one` removed")

    def test_execute_not_found(self, empty_options, empty_suboptions,
                               test_data_source, nonedefault_store):
        empty_options.store = nonedefault_store.path
        with patch("__builtin__.print") as print_patched:
            DataSourceRmCommand.execute(empty_options, empty_suboptions, "xxxx")
            print_patched.assert_called_with("Datasource `xxxx` not found, NOT REMOVED")

    def test_invalid_params(self, empty_options, empty_suboptions, test_data_source,
                            nonedefault_store):
        empty_options.store = nonedefault_store.path
        # DataSource takes one param
        with pytest.raises(InvalidParams):
            DataSourceRmCommand.execute(empty_options, empty_suboptions)


class TestDataSourceTest(object):
    def test_execute(self, empty_options, empty_suboptions, test_data_source, nonedefault_store):
        test_data_source.test.return_value = True
        empty_options.store = nonedefault_store.path
        DataSourceTestCommand.execute(empty_options, empty_suboptions, "datasource one")
        test_data_source.test.assert_called

    def test_execute_not_found(self, empty_options, empty_suboptions,
                               test_data_source, nonedefault_store):
        empty_options.store = nonedefault_store.path
        with patch("__builtin__.print") as print_patched:
            DataSourceTestCommand.execute(empty_options, empty_suboptions, "xxxx")
            print_patched.assert_called_with("Datasource `xxxx` not found, NOT TESTED")

    def test_invalid_params(self, empty_options, empty_suboptions, test_data_source,
                            nonedefault_store):
        empty_options.store = nonedefault_store.path
        # DataSource takes one param
        with pytest.raises(InvalidParams):
            DataSourceTestCommand.execute(empty_options, empty_suboptions)


class TestDataSourceAdd(object):
    def test_execute(self, empty_options, empty_suboptions, test_data_source, nonedefault_store):
        empty_options.store = nonedefault_store.path
        test_data_source.test.return_value = True
        command = build_datasource_add_type(test_data_source)
        command.execute(empty_options, empty_suboptions, "test name", 1, 2)
        assert len(nonedefault_store.datasources(name="test name")) == 1

    def test_execute_service_unavailable(self, empty_options, empty_suboptions, test_data_source,
                                         nonedefault_store):
        empty_options.store = nonedefault_store.path
        test_data_source.test.return_value = False
        empty_suboptions.no_test = False
        command = build_datasource_add_type(test_data_source)
        with patch("__builtin__.print") as print_patched:
            command.execute(empty_options, empty_suboptions, "test name 2", 1, 2)
            assert len(nonedefault_store.datasources(name="test name 2")) == 0
            print_patched.assert_called_with(
                    "THIS DATA SOURCE NOT BE ADDED, use --no-test flag to add it even")

    def test_execute_test_disabled(self, empty_options, empty_suboptions, test_data_source,
                                   nonedefault_store):
        empty_options.store = nonedefault_store.path
        test_data_source.test.return_value = False
        empty_suboptions.not_test = True
        command = build_datasource_add_type(test_data_source)
        command.execute(empty_options, empty_suboptions, "test name", 1, 2)
        assert len(nonedefault_store.datasources(name="test name")) == 1

    def test_invalid_params(self, empty_options, empty_suboptions, test_data_source):
        command = build_datasource_add_type(test_data_source)
        with pytest.raises(InvalidParams):
            command.execute(empty_options, empty_suboptions)


class TestDataSourceEcho(object):
    def test_execute(self, empty_options, empty_suboptions, test_data_source):
        # otupus returns a hardcoded name and the type of the
        # datasource along with the expected keys of datasource
        output = {
            'type': 'test',
            'name': 'stdout',
            'foo': 1,
            'bar': 2
        }
        command = build_datasource_echo_type(test_data_source)
        with patch("__builtin__.print") as print_patched:
            command.execute(empty_options, empty_suboptions, 1, 2)
            print_patched.assert_called_with(dumps(output))

    def test_invalid_params(self, empty_options, empty_suboptions, test_data_source):
        # test_data_source takes two params
        command = build_datasource_echo_type(test_data_source)
        with pytest.raises(InvalidParams):
            command.execute(empty_options, empty_suboptions, 1)


class TestDataSourceList(object):
    def test_execute(self, empty_options, empty_suboptions, test_data_source, nonedefault_store):
        empty_options.store = nonedefault_store.path
        with patch("__builtin__.print") as print_patched:
            DataSourceListCommand.execute(empty_options, empty_suboptions)
            print_patched.assert_called_with("Datasource `datasource two` (test)")


class TestQueryCommand(object):
    @patch("gramola.commands.sys")
    @patch("gramola.commands.Plot")
    def test_execute_stdin(self, plot_patched, sys_patched, empty_options, empty_suboptions,
                           test_data_source):
        empty_suboptions.refresh = False
        datapoints = [(1, 0), (2, 1), (3, 1)]
        buffer_ = dumps({'type': 'test', 'name': 'stdout', 'foo': 1, 'bar': 1})
        sys_patched.stdin.read.return_value = buffer_

        test_data_source.datapoints.return_value = datapoints
        command = build_datasource_query_type(test_data_source)
        command.execute(empty_options, empty_suboptions, "-", "foo", "-1d", "now")
        plot_patched.return_value.draw.assert_called_with(datapoints)

        test_data_source.datapoints.assert_call_with(
            test_data_source.METRIC_QUERY_CLS(metric='foo', since='-1d', until='now')
        )

    @patch("gramola.commands.sys")
    def test_invalid_params(self, sys_patched, empty_options, empty_suboptions, test_data_source):
        # query test_data_source takes four required params
        buffer_ = dumps({'type': 'test', 'name': 'stdout', 'foo': 1, 'bar': 1})
        sys_patched.stdin.read.return_value = buffer_
        command = build_datasource_echo_type(test_data_source)
        with pytest.raises(InvalidParams):
            command.execute(empty_options, empty_suboptions, "-")
