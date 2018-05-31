import unittest

import boto3

from trading_platform.core.services.alert_service import AlertService


class TestAlertService(unittest.TestCase):
    def test_aws_sns_client(self):
        alert_service = AlertService(boto3.client('sns'))
        alert_msg = 'test_alert'
        alert_service.send_alert('arn:aws:sns:us-west-1:207283649878:arbitrage-alerts', alert_msg)