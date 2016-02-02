# -*- coding: utf-8 -*-
"""
Implements the Grahpite [1] data source.

[1] https://graphite.readthedocs.org/en/latest/
:moduleauthor: Pau Freixes, pfreixes@gmail.com
"""
import requests

from gramola import log
from requests.exceptions import RequestException

from gramola.datasources.base import (
    OptionalKey,
    DataSource,
    MetricQuery,
    DataSourceConfig
)


class GraphiteDataSourceConfig(DataSourceConfig):
    REQUIRED_KEYS = ('url',)
    OPTIONAL_KEYS = ()


class GraphiteMetricQuery(MetricQuery):
    REQUIRED_KEYS = ()
    OPTIONAL_KEYS = (
        OptionalKey('since', 'Get values from, default -1h'),
        OptionalKey('until', 'Get values until, default now')
    )


class GraphiteDataSource(DataSource):
    DATA_SOURCE_CONFIGURATION_CLS = GraphiteDataSourceConfig
    METRIC_QUERY_CLS = GraphiteMetricQuery 
    TYPE = 'graphite'

    def _safe_request(self, url, params):
        try:
            response = requests.get(url, params=params)
        except RequestException, e:
            log.warning("Something was wrong with Graphite service")
            log.debug(e)
            return None

        if response.status_code != 200:
            log.warning("Get a invalid {} HTTP code from Grahpite service".format(response.status_code))
            return None

        return response.json()


    def suggestions(self, current, key='name'):
        if key != 'name':
            return []

        # Graphite publihes the `/metrics/find` API endpoint to retrieve the
        # availabe metrics path from a given value.
        query = "*" if not current else current + "*"

        if self.configuration.url[-1] != '/':
            url = self.configuration.url + '/metrics/find' 
        else:
            url = self.configuration.url + 'metrics/find' 

        params = {'query': query}

        response = self._safe_request(url, params)
        if not response:
            return []

        return [path['text'] for path in response]
        

    def datapoints(self, query, maxdatapoints=None):
        # Graphite publisheds the endpoint `/render` to retrieve
        # datapoins from one or mulitple targets, we make sure that
        # only retrieve one target at once, Gramola supports only
        # rendering of one target.

        params = {
            'target': query.metric,

            # default window timme used if no params given
            # is datapoints from the last 1 hour
            'from': query.since or '-1h',
            'to': query.until or 'now',

            # graphite supports mulitple output format, we have
            # to configure the json output
            'format': 'json'
        }

        if maxdatapoints:
            params['maxDataPoints'] = maxdatapoints

        if self.configuration.url[-1] != '/':
            url = self.configuration.url + '/render' 
        else: 
            url = self.configuration.url + 'render'

        response = self._safe_request(url, params)

        if response is None:
            return []
        elif len(response) == 0:
            log.warning('Metric `{}` not found'.format(query.metric))
            return []
        elif len(response) > 1:
            log.warning('Multiple metrics found, geting only the first one')

        # Graphite returns a list of lists, we turn it into a list of tuples to
        # make it compatible with the datapoints return type.

        # FIXME: Gramola not supports None values because we change None values from None
        # to 0.
        return [(col[0] or 0, col[1]) for col in response[0]["datapoints"]]
 

    def test(self):
        # test using the metrics find endpoint
        url = self.configuration.url + '/metrics/find' 
        try:
            response = requests.get(url, params={'query': '*'})
        except RequestException, e:
            log.debug('Test failed request error {}'.format(e))
            return False

        return True
