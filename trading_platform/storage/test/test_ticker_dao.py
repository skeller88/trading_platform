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
from trading_platform.utils.datetime_operations import utc_timestamp
from trading_platform.core.test import data

SECONDS_PER_MIN = 60
SECONDS_PER_DAY = SECONDS_PER_MIN*60*24
TICKER_VERSION = 0


class TestTickerDao(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pair = Pair(base='BTC', quote='XRP')
        cls.engine = SqlAlchemyEngine.local_engine_maker()
        cls.engine.initialize_tables()
        cls.session = cls.engine.scoped_session_maker()
        cls.ticker_dao = TickerDao()

    def setUp(self):
        now = utc_timestamp()
        tickers = data.time_ordered_tickers()
        self.ticker1 = tickers[0]
        self.ticker2 = tickers[1]

    def tearDown(self):
        self.ticker_dao.delete_all(session=self.session)
        self.session.commit()
        self.session.close_all()

    @classmethod
    def tearDownClass(cls):
        cls.engine.drop_tables()

    # Create
    def test_save_and_commit(self):
        session, created = self.ticker_dao.save(session=self.session, commit=True, popo=self.ticker1)
        assert_true(created.db_id)
        assert_true(created.processing_time)
        self.ticker1.db_id = created.db_id
        eq_(created, self.ticker1)

    @raises(sqlalchemy.exc.ProgrammingError)
    def test_save_with_missing_fields_throws_constraint_violation_(self):
        self.ticker1.ask = None
        self.ticker_dao.save(session=self.session, commit=True, popo=self.ticker1)

    def test_bulk_save_and_commit(self):
        session, created = self.ticker_dao.bulk_save(session=self.session, commit=True, popos=[self.ticker1, self.ticker2])
        eq_(len(created), 2)

        for ticker in created:
            assert_true(ticker.db_id)
            assert_true(ticker.event_time)
            assert_true(ticker.last)
            assert_true(ticker.processing_time)
            eq_(ticker.base, self.ticker1.base)
            eq_(ticker.quote, self.ticker1.quote)
            eq_(ticker.version, Ticker.current_version)

    # Read
    def test_fetch_by_id(self):
        session, created = self.ticker_dao.save(session=self.session, commit=True, popo=self.ticker1)
        session, fetched = self.ticker_dao.fetch_by_db_id(self.session, created.db_id)
        eq_(fetched, created)

    def test_fetch_by_nonexistent_id(self):
        session, fetched = self.ticker_dao.fetch_by_db_id(self.session, int(utc_timestamp()))
        eq_(fetched, None)

    def test_fetch_by_event_time_between_range(self):
        session, created = self.ticker_dao.bulk_save(session=self.session, commit=True,
                                                     popos=[self.ticker1, self.ticker2])

        # start time > event_time of all tickers. Should return no tickers.
        session, fetched = self.ticker_dao.fetch_by_event_time_between_range(start=(self.ticker2.event_time +
                                                                                    SECONDS_PER_MIN),
                                                                             end=utc_timestamp(), session=self.session)
        eq_(0, len(fetched))

        session, fetched = self.ticker_dao.fetch_by_event_time_between_range(start=self.ticker2.event_time,
                                                                    end=self.ticker2.event_time + SECONDS_PER_MIN,
                                                                             session=self.session)
        eq_(1, len(fetched))

        session, fetched = self.ticker_dao.fetch_by_event_time_between_range(start=self.ticker1.event_time,
                                                                    end=self.ticker2.event_time + SECONDS_PER_MIN,
                                                                             session=self.session)
        eq_(2, len(fetched))

    def test_fetch_by_event_time_gte_range(self):
        session, created = self.ticker_dao.bulk_save(session=self.session, commit=True,
                                                     popos=[self.ticker1, self.ticker2])

        # start time > event_time of all tickers. Should return no tickers.
        session, fetched = self.ticker_dao.fetch_by_event_time_gte_range(start=self.ticker2.event_time + SECONDS_PER_MIN,
                                                                         session=self.session)
        eq_(0, len(fetched))

        session, fetched = self.ticker_dao.fetch_by_event_time_gte_range(start=self.ticker2.event_time, session=self.session)
        eq_(1, len(fetched))

        session, fetched = self.ticker_dao.fetch_by_event_time_gte_range(start=self.ticker1.event_time, session=self.session)
        eq_(2, len(fetched))

    # Delete
    def test_delete(self):
        session, created = self.ticker_dao.bulk_save(session=self.session, commit=True,
                                                     popos=[self.ticker1, self.ticker2])
        eq_(len(created), 2)
        session, deleted = self.ticker_dao.delete_all(session=self.session, commit=True)
        eq_(deleted, 2)