import pytest

from mock import patch, Mock
from requests.exceptions import RequestException

from gramola.utils import parse_date
from gramola.datasources.graphite import (
    DATE_FORMAT,
    GraphiteDataSource,
    GraphiteMetricQuery
)

REQUESTS = 'gramola.datasources.graphite.requests'


@pytest.fixture
def config():
    return GraphiteDataSource.DATA_SOURCE_CONFIGURATION_CLS(**{
        'type': 'graphite',
        'name': 'datasource name',
        'url': 'http://localhost:9000'
    })


@patch(REQUESTS)
class TestSuggestions(object):
    def test_name_suggestion(self, prequests, config):
        response = Mock()
        response.status_code = 200
        response.json.return_value = [{'text': 'foo'}, {'text': 'bar'}]
        prequests.get.return_value = response
        graphite = GraphiteDataSource(config)
        assert graphite.suggestions(None) == ['foo', 'bar']
        prequests.get.assert_called_with(
            'http://localhost:9000/metrics/find',
            params={'query': '*'})

        assert graphite.suggestions('suffix') == ['foo', 'bar']
        prequests.get.assert_called_with(
            'http://localhost:9000/metrics/find',
            params={'query': 'suffix*'})

    def test_requests_exception(self, prequests, config):
        prequests.get.side_effect = RequestException()
        graphite = GraphiteDataSource(config)
        assert graphite.suggestions(None) == []

    def test_requests_exception(self, prequests, config):
        response = Mock()
        response.status_code = 500
        prequests.get.return_value = response
        graphite = GraphiteDataSource(config)
        assert graphite.suggestions(None) == []


@patch(REQUESTS)
class TestTest(object):
    def test_requests_exception(self, prequests, config):
        prequests.get.side_effect = RequestException()
        graphite = GraphiteDataSource(config)
        assert graphite.test() == False

    def test_ok(self, prequests, config):
        response = Mock()
        response.status_code = 200
        prequests.get.return_value = response
        graphite = GraphiteDataSource(config)
        assert graphite.test() == True


@patch(REQUESTS)
class TestDatapoints(object):
    @pytest.fixture
    def query(self):
        return GraphiteDataSource.METRIC_QUERY_CLS(**{
            'target': 'foo.bar',
            'since': '-24h',
            'until': '-12h'
        })

    def test_query(self, prequests, config, query):
        response = Mock()
        response.status_code = 200
        response.json.return_value = [{
            'target': 'foo.bar',
            'datapoints': [[1, 1451391760]]
        }]
        prequests.get.return_value = response
        graphite = GraphiteDataSource(config)
        assert graphite.datapoints(query) == [(1, 1451391760)]
        prequests.get.assert_called_with(
            'http://localhost:9000/render',
            params={'target': 'foo.bar',
                    'from': parse_date('-24h').strftime(DATE_FORMAT),
                    'to': parse_date('-12h').strftime(DATE_FORMAT),
                    'format': 'json'}
        )

    def test_query_default_values(self, prequests, config):
        response = Mock()
        response.status_code = 200
        response.json.return_value = [{
            'target': 'foo.bar',
            'datapoints': [[1, 1451391760]]
        }]
        prequests.get.return_value = response
        graphite = GraphiteDataSource(config)

        # build the mvp of query to be filled with the default ones
        query = GraphiteDataSource.METRIC_QUERY_CLS(**{
            'target': 'foo.bar'
        })

        assert graphite.datapoints(query) == [(1, 1451391760)]
        prequests.get.assert_called_with(
            'http://localhost:9000/render',
            params={'target': 'foo.bar',
                    'from': parse_date('-1h').strftime(DATE_FORMAT),
                    'to': parse_date('now').strftime(DATE_FORMAT),
                    'format': 'json'}
        )

    def test_query_remove_last_None(self, prequests, config):
        response = Mock()
        response.status_code = 200
        response.json.return_value = [{
            'target': 'foo.bar',
            'datapoints': [[1, 1451391760], [None, 1451391770]]
        }]
        prequests.get.return_value = response
        graphite = GraphiteDataSource(config)

        # build the mvp of query to be filled with the default ones
        query = GraphiteDataSource.METRIC_QUERY_CLS(**{
            'target': 'foo.bar'
        })

        assert graphite.datapoints(query) == [(1, 1451391760)]

    def test_requests_exception(self, prequests, config, query):
        prequests.get.side_effect = RequestException()
        graphite = GraphiteDataSource(config)
        assert graphite.datapoints(query) == []
