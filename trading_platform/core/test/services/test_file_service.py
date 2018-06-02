import datetime
import unittest
from typing import Generator, List

from nose.tools import eq_

from trading_platform.core.services.file_service import FileService
from trading_platform.utils.datetime_operations import strftime_minutes


class TestFileService(unittest.TestCase):
    def test_datetime_generator_by_day(self):
        start_datetime: datetime.datetime = datetime.datetime(2018, 1, 1)
        end_datetime: datetime.datetime = datetime.datetime(2018, 2, 1)
        timedelta: datetime.timedelta = datetime.timedelta(days=1)
        generator: Generator[datetime.datetime, None, None] = FileService.datetime_generator(start_datetime, end_datetime, timedelta)
        dts: List[datetime.datetime] = list(map(lambda x: x, generator))
        eq_(len(dts), 31)
        eq_(dts[0].strftime(strftime_minutes), start_datetime.strftime(strftime_minutes))
        end_datetime_inclusive: datetime.datetime = datetime.datetime(2018, 1, 31)
        eq_(dts[-1].strftime(strftime_minutes), end_datetime_inclusive.strftime(strftime_minutes))

    def test_datetime_generator_by_hour(self):
        start_datetime: datetime.datetime = datetime.datetime(2018, 1, 1)
        end_datetime: datetime.datetime = datetime.datetime(2018, 1, 1, 8)
        timedelta: datetime.timedelta = datetime.timedelta(hours=1)
        generator: Generator[datetime.datetime, None, None] = FileService.datetime_generator(start_datetime, end_datetime, timedelta)
        dts: List[datetime.datetime] = list(map(lambda x: x, generator))
        eq_(len(dts), 8)
        eq_(dts[0].strftime(strftime_minutes), start_datetime.strftime(strftime_minutes))
        end_datetime_inclusive: datetime.datetime = datetime.datetime(2018, 1, 1, 7)
        eq_(dts[-1].strftime(strftime_minutes), end_datetime_inclusive.strftime(strftime_minutes))