import pytest
import time

from mock import patch, Mock

from gramola.store import (
    NotFound,
    DuplicateEntry,
    Store
)

from .fixtures import test_data_source

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


class TestStore(object):
    def test_datasources(self, nonedefault_store, test_data_source):
        datasources = nonedefault_store.datasources()
        assert len(datasources) == 2

        # just check the second result
        assert type(datasources[1]) == test_data_source.DATA_SOURCE_CONFIGURATION_CLS
        assert datasources[1].type == "test"
        assert datasources[1].name == "datasource two"
        assert datasources[1].foo == "c"
        assert datasources[1].bar == "d"
        assert datasources[1].gramola == "e"

    def test_datasources_filter_name(self, nonedefault_store, test_data_source):
        datasources = nonedefault_store.datasources(name="datasource two")
        assert len(datasources) == 1

    def test_datasources_filter_type(self, nonedefault_store, test_data_source):
        datasources = nonedefault_store.datasources(type_="notimplemented")
        assert len(datasources) == 0

    def test_add_datasource(self, nonedefault_store, test_data_source):
        params = {"type": "test", "name": "test name", "foo": "a", "bar": "b"}
        config = test_data_source.DATA_SOURCE_CONFIGURATION_CLS(**params)
        nonedefault_store.add_datasource(config)
        assert len(nonedefault_store.datasources(name="test name")) == 1

    def test_add_duplicate_datasource(self, nonedefault_store, test_data_source):
        # datasource one already exist as a part of the fixture
        params = {"type": "test", "name": "datasource one", "foo": "a", "bar": "b"}
        config = test_data_source.DATA_SOURCE_CONFIGURATION_CLS(**params)
        with pytest.raises(DuplicateEntry):
            nonedefault_store.add_datasource(config)

    def test_rm_datasource(self, nonedefault_store, test_data_source):
        assert len(nonedefault_store.datasources()) == 2
        # remove one of the datasources of the fixture
        nonedefault_store.rm_datasource("datasource one")
        assert len(nonedefault_store.datasources()) == 1

    def test_rm_notfound_datasource(self, nonedefault_store, test_data_source):
        with pytest.raises(NotFound):
            nonedefault_store.rm_datasource("xxxx")
