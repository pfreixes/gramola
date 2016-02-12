import pytest

from mock import patch, Mock, MagicMock, ANY
from datetime import datetime
from datetime import timedelta

from botocore.exceptions import (
    PartialCredentialsError,
    NoRegionError,
    ClientError,
)
from gramola.datasources.cloudwatch import (
    Boto3ClientError,
    CWDataSource,
    CWMetricQuery
)
from gramola.datasources.base import InvalidMetricQuery

BOTO3 = 'gramola.datasources.cloudwatch.boto3'


@pytest.fixture
def config():
    return CWDataSource.DATA_SOURCE_CONFIGURATION_CLS(**{
        'type': 'cw',
        'name': 'cw',
    })


@pytest.fixture
def config_options():
    return CWDataSource.DATA_SOURCE_CONFIGURATION_CLS(**{
        'type': 'cw',
        'name': 'cw',
        'region': 'eu-west-1',
        'profile': 'sandbox',
    })


@patch(BOTO3)
class TestBotoClient(object):
    # Test the method _cw_client
    def test_cw_client(self, boto3, config):
        cw = CWDataSource(config)
        cw._cw_client()
        boto3.session.Session.called_with(None, None)

    def test_cw_client_opitons(self, boto3, config_options):
        cw = CWDataSource(config_options)
        cw._cw_client()
        boto3.session.Session.called_with(region_name='eu-west-1', profile_name='sandbox')

    def test_raises_boto3clienterror(self, boto3, config):
        boto3.session.Session.side_effect = PartialCredentialsError(provider=Mock(),
                                                                    cred_var=Mock())
        with pytest.raises(Boto3ClientError):
            CWDataSource(config)._cw_client()
        boto3.session.Session.side_effect = ClientError(MagicMock(), Mock())
        with pytest.raises(Boto3ClientError):
            CWDataSource(config)._cw_client()
        boto3.session.Session.side_effect = NoRegionError()
        with pytest.raises(Boto3ClientError):
            CWDataSource(config)._cw_client()


@patch(BOTO3)
class TestTest(object):
    def test_boto3_raises_exceptions_fail(self, boto3, config):
        boto3.session.Session.side_effect = PartialCredentialsError(provider=Mock(),
                                                                    cred_var=Mock())
        assert CWDataSource(config).test() == False
        boto3.session.Session.side_effect = ClientError(MagicMock(), Mock())
        assert CWDataSource(config).test() == False
        boto3.session.Session.side_effect = NoRegionError()
        assert CWDataSource(config).test() == False

    def test_ok(self, boto3, config):
        cw = CWDataSource(config)
        assert cw.test() == True


@patch(BOTO3)
class TestDatapoints(object):
    @pytest.fixture
    def query_dict(self):
        return {
            'namespace': 'AWS/EC2',
            'metricname': 'CPUUtillization',
            'dimension_name': 'AutoScalingGroupName',
            'dimension_value': 'foo',
            'until': datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
            'since': (datetime.now() - timedelta(hours=12)).strftime('%Y-%m-%dT%H:%M:%S')
        }

    @pytest.fixture
    def response(self):
        return {
            'Label': 'foo',
            'Datapoints': [
                {'Timestamp': datetime.now(), 'SampleCount': 1,
                 'Average': 1, 'Sum': '11', 'Minimum': 1, 'Maximum': 1, 'Unit': 'foos'},
                {'Timestamp': datetime.now(), 'SampleCount': 2,
                 'Average': 2, 'Sum': '22', 'Minimum': 2, 'Maximum': 2, 'Unit': 'foos'}
            ]
        }

    def test_query(self, boto3, config, query_dict, response):
        query = CWDataSource.METRIC_QUERY_CLS(**query_dict)
        boto3.session.Session.return_value.client.return_value.\
            get_metric_statistics.return_value = response
        cw = CWDataSource(config)
        datapoints = cw.datapoints(query)
        assert len(datapoints) == len(response['Datapoints'])
        for idx, i in enumerate(datapoints):
            assert i[0] == response['Datapoints'][idx]['Average']
            assert i[0] == response['Datapoints'][idx]['Average']

        boto3.session.Session.return_value.client.return_value.\
            get_metric_statistics.assert_called_with(
                Namespace='AWS/EC2', MetricName='CPUUtillization',
                StartTime=datetime.strptime(query.since, '%Y-%m-%dT%H:%M:%S'),
                EndTime=datetime.strptime(query.until, '%Y-%m-%dT%H:%M:%S'), Period=60,
                Dimensions=[{'Name': 'AutoScalingGroupName', 'Value': 'foo'}],
                Statistics=['Average']
            )

    def test_query_sum(self, boto3, config, query_dict, response):
        query_dict.update({'statistics': 'Sum'})
        query = CWDataSource.METRIC_QUERY_CLS(**query_dict)
        boto3.session.Session.return_value.client.return_value.\
            get_metric_statistics.return_value = response
        cw = CWDataSource(config)
        datapoints = cw.datapoints(query)
        assert len(datapoints) == len(response['Datapoints'])
        for idx, i in enumerate(datapoints):
            assert i[0] == response['Datapoints'][idx]['Sum']
            assert i[0] == response['Datapoints'][idx]['Sum']

        boto3.session.Session.return_value.client.return_value.\
            get_metric_statistics.assert_called_with(
                Namespace='AWS/EC2', MetricName='CPUUtillization',
                StartTime=datetime.strptime(query.since, '%Y-%m-%dT%H:%M:%S'),
                EndTime=datetime.strptime(query.until, '%Y-%m-%dT%H:%M:%S'), Period=60,
                Dimensions=[{'Name': 'AutoScalingGroupName', 'Value': 'foo'}],
                Statistics=['Sum']
            )

    def test_query_invalid_statistics(self, boto3, config, query_dict, response):
        query_dict.update({'statistics': 'foo'})
        query = CWDataSource.METRIC_QUERY_CLS(**query_dict)
        cw = CWDataSource(config)
        with pytest.raises(InvalidMetricQuery):
            datapoints = cw.datapoints(query)

    def test_query_maxdatapoints(self, boto3, config, query_dict):
        query = CWDataSource.METRIC_QUERY_CLS(**query_dict)
        cw = CWDataSource(config)
        datapoints = cw.datapoints(query, maxdatapoints=100)

        boto3.session.Session.return_value.client.return_value.\
            get_metric_statistics.assert_called_with(
                Namespace='AWS/EC2', MetricName='CPUUtillization',
                StartTime=datetime.strptime(query.since, '%Y-%m-%dT%H:%M:%S'),
                EndTime=datetime.strptime(query.until, '%Y-%m-%dT%H:%M:%S'), Period=480,
                Dimensions=[{'Name': 'AutoScalingGroupName', 'Value': 'foo'}],
                Statistics=['Average']
            )
