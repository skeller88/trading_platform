"""
nosetests test.storage.test_tickers_crud --nocapture
"""
import unittest

import sqlalchemy
from nose.tools import assert_true, eq_, raises

from trading_platform.exchanges.data.pair import Pair
from trading_platform.exchanges.data.ticker import Ticker
from trading_platform.storage.daos.ticker_dao import TickerDao
from trading_platform.storage.sql_alchemy_engine import SqlAlchemyEngine
from trading_platform.storage.test.test_dao import TestDao
from trading_platform.utils.datetime_operations import utc_timestamp
from trading_platform.core.test import data

SECONDS_PER_MIN = 60
SECONDS_PER_DAY = SECONDS_PER_MIN*60*24
TICKER_VERSION = 0


class TestTickerDao(TestDao):
    __test__ = True  # important, makes sure tests are not run on base class
    dao_class = TickerDao
    popo_class = Ticker

    def setUp(self):
        now = utc_timestamp()
        tickers = data.time_ordered_tickers()
        self.dto1 = tickers[0]
        self.dto2 = tickers[1]

    def test_fetch_by_event_time_between_range(self):
        created = self.dao.bulk_save(session=self.session, commit=True,
                                                     popos=[self.dto1, self.dto2])

        # start time > event_time of all tickers. Should return no tickers.
        fetched = self.dao.fetch_by_event_time_between_range(start=(self.dto2.event_time +
                                                                                    SECONDS_PER_MIN),
                                                                             end=utc_timestamp(), session=self.session)
        eq_(0, len(fetched))

        fetched = self.dao.fetch_by_event_time_between_range(start=self.dto2.event_time,
                                                                    end=self.dto2.event_time + SECONDS_PER_MIN,
                                                                             session=self.session)
        eq_(1, len(fetched))

        fetched = self.dao.fetch_by_event_time_between_range(start=self.dto1.event_time,
                                                                    end=self.dto2.event_time + SECONDS_PER_MIN,
                                                                             session=self.session)
        eq_(2, len(fetched))

    def test_fetch_by_event_time_gte_range(self):
        created = self.dao.bulk_save(session=self.session, commit=True,
                                                     popos=[self.dto1, self.dto2])

        # start time > event_time of all tickers. Should return no tickers.
        fetched = self.dao.fetch_by_event_time_gte_range(start=self.dto2.event_time + SECONDS_PER_MIN,
                                                                         session=self.session)
        eq_(0, len(fetched))

        fetched = self.dao.fetch_by_event_time_gte_range(start=self.dto2.event_time, session=self.session)
        eq_(1, len(fetched))

        fetched = self.dao.fetch_by_event_time_gte_range(start=self.dto1.event_time, session=self.session)
        eq_(2, len(fetched))
