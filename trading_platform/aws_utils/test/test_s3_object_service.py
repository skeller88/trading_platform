import datetime
import os
import unittest

from nose.tools import eq_

from trading_platform.aws_utils.s3_object_service import S3ObjectService
from trading_platform.core.services.file_service import FileService
from trading_platform.exchanges.data.ticker import Ticker


class TestS3ObjectService(unittest.TestCase):
    def test_window_ticker_objects(self):
        s3_object_service = S3ObjectService(object_version='4')
        output_dir = os.path.join(os.getcwd(), 'tmp_test_data')
        FileService.create_dir_if_null(output_dir)
        start_datetime = datetime.datetime(2018, 5, 1, 0)
        end_datetime = datetime.datetime(2018, 5, 1, 10)
        timedelta = datetime.timedelta(minutes=5)
        s3_object_service.window_objects(output_dir=output_dir, start_datetime=start_datetime,
                                         end_datetime=end_datetime, timedelta=timedelta,
                                         multithreading=True)
        files = os.listdir(output_dir)
        eq_(len(files), 2)