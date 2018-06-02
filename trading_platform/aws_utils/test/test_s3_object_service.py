import datetime
import os
import shutil
import unittest

import pandas
from nose.tools import eq_

from trading_platform.aws_utils.s3_object_service import S3ObjectService
from trading_platform.core.services.file_service import FileService
from trading_platform.core.test.util_methods import disable_debug_logging
from trading_platform.exchanges.data.ticker import Ticker
from trading_platform.utils.datetime_operations import strftime_minutes, strftime_hours


class TestS3ObjectService(unittest.TestCase):
    def test_window_ticker_objects_by_5_minutes(self):
        disable_debug_logging()
        s3_object_service = S3ObjectService(object_version='4', max_workers=1500)
        output_dir = os.path.join(os.getcwd(), 'tmp_test_data')
        FileService.create_dir_if_null(output_dir)
        start_datetime = datetime.datetime(2018, 5, 1, 0)
        # 10 minutes later
        end_datetime = datetime.datetime(2018, 5, 1, 0, 10)
        timedelta = datetime.timedelta(minutes=5)
        s3_object_service.window_objects(output_dir=output_dir, start_datetime=start_datetime,
                                         end_datetime=end_datetime, timedelta=timedelta, strftime=strftime_minutes,
                                         multithreading=True)
        files = os.listdir(output_dir)
        eq_(len(files), 2)
        eq_(df.columns, Ticker.csv_fieldnames())
        shutil.rmtree(output_dir, ignore_errors=True)

    def test_window_ticker_objects_by_hour(self):
        """
        Test fetching a larger amount of data.
        Returns:

        """
        disable_debug_logging()
        s3_object_service = S3ObjectService(object_version='4', max_workers=1500)
        output_dir = os.path.join(os.getcwd(), 'tmp_test_data')
        FileService.create_dir_if_null(output_dir)
        start_datetime = datetime.datetime(2018, 5, 1, 0)
        # 2 hours later
        end_datetime = datetime.datetime(2018, 5, 1, 2)
        timedelta = datetime.timedelta(hours=1)
        s3_object_service.window_objects(output_dir=output_dir, start_datetime=start_datetime,
                                         end_datetime=end_datetime, timedelta=timedelta, strftime=strftime_hours,
                                         multithreading=True)
        files = os.listdir(output_dir)
        eq_(len(files), 2)
        df = pandas.read_csv(files[0])
        eq_(df.columns, Ticker.csv_fieldnames())
        shutil.rmtree(output_dir, ignore_errors=True)