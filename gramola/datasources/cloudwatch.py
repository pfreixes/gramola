# -*- coding: utf-8 -*-
"""
Implements the CloudWatch [1] data source.

[1] https://aws.amazon.com/cloudwatch/
:moduleauthor: Pau Freixes, pfreixes@gmail.com
"""
import time
import boto3
import botocore

from functools import wraps
from itertools import count
from itertools import dropwhile

from gramola import log

from gramola.datasources.base import (
    OptionalKey,
    DataSource,
    MetricQuery,
    DataSourceConfig,
    InvalidMetricQuery
)


class Boto3ClientError(Exception):
    # Global class used to trigger all Exceptions related
    # with the Boto3 client.
    pass


def _cw_safe_call(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except botocore.exceptions.ClientError, e:
            raise Boto3ClientError("Client eroor {}".format(str(e)))
        except botocore.exceptions.PartialCredentialsError, e:
            raise Boto3ClientError("Partial Credentials error {}".format(str(e)))
        except botocore.exceptions.NoRegionError:
            raise Boto3ClientError("No default region, give one using the --region option")
    return wrapper


class CWDataSourceConfig(DataSourceConfig):
    REQUIRED_KEYS = ()
    OPTIONAL_KEYS = (
        OptionalKey('region', 'Use this region as the default one insted of the' +
                              ' region defined by the profile'),
        OptionalKey('profile', 'Use an alternative profile than the default one')
    )


class CWMetricQuery(MetricQuery):
    REQUIRED_KEYS = ('namespace', 'metricname', 'dimension_name', 'dimension_value')
    OPTIONAL_KEYS = (
        OptionalKey('region', 'Use this region overriding the region configured by the ' +
                              ' datasource or profile'),
        OptionalKey('statistics', 'Override the default Average by Sum, SampleCount, '
                                  'Maximum or Minimum')
    )


class CWDataSource(DataSource):
    DATA_SOURCE_CONFIGURATION_CLS = CWDataSourceConfig
    METRIC_QUERY_CLS = CWMetricQuery
    TYPE = 'cw'

    @_cw_safe_call
    def _cw_client(self, region=None):
        return boto3.session.Session(
            region_name=region or self.configuration.region,
            profile_name=self.configuration.profile).client('cloudwatch')

    @_cw_safe_call
    def _cw_call(self, client, f, *args, **kwargs):
        return getattr(client, f)(*args, **kwargs)

    def suggestions(self, current, key='name'):
        raise NotImplemented()

    def datapoints(self, query, maxdatapoints=None):
        if query.statistics and (query.statistics not in ['Average', 'Sum', 'SampleCount',
                                                          'Maximum', 'Minimum']):
            raise InvalidMetricQuery("Query statistic invalid value `{}`".format(query.statistics))
        elif query.statistics:
            statistics = query.statistics
        else:
            statistics = "Average"

        if maxdatapoints:
            # Calculate the Period where the number of datapoints
            # returned are less than maxdatapoints.

            # Get the first granularity that suits for return the maxdatapoints
            seconds = (query.get_until() - query.get_since()).total_seconds()
            period = next(dropwhile(lambda g: seconds / g > maxdatapoints, count(60, 60)))
        else:
            period = 60

        # get a client using the region given by the query, or if it
        # is None using the one given by the datasource or the profile
        client = self._cw_client(region=query.region)

        kwargs = {
            'Namespace': query.namespace,
            'MetricName': query.metricname,
            'StartTime': query.get_since(),
            'EndTime': query.get_until(),
            'Period': period,
            'Dimensions': [{
                'Name': query.dimension_name,
                'Value': query.dimension_value,
            }],
            'Statistics': [statistics]
        }

        datapoints = self._cw_call(client, "get_metric_statistics", **kwargs)
        return [(point[statistics], time.mktime(point['Timestamp'].timetuple()))
                for point in datapoints['Datapoints']]

    def test(self):
        # Just test creating the boto client and trying to get the list of
        # available metrics.
        try:
            self._cw_call(self._cw_client(), "list_metrics")
        except Boto3ClientError, e:
            log.error("Boto3 client got an exception: {}".format(e.message))
            return False
        return True
