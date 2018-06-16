"""
nosetests test.storage.test_order_dao --nocapture
"""
import math

from nose.tools import eq_, assert_greater

from trading_platform.core.test import data
from trading_platform.core.test.util_methods import eq_ignore_certain_fields
from trading_platform.exchanges.data.enums import exchange_ids
from trading_platform.exchanges.data.order import Order
from trading_platform.storage.daos.order_dao import OrderDao
from trading_platform.storage.test.test_dao import TestDao


class TestOrderDao(TestDao):
    __test__ = True  # important, makes sure tests are not run on base class
    dao_class = OrderDao
    popo_class = Order

    def setUp(self):
        self.dto1 = data.order(exchange_ids.binance)
        self.dto2 = data.order(exchange_ids.bittrex, processing_time=self.dto1.processing_time + 5000.)

    def test_fetch_by_order_id(self):
        self.dao.save(session=self.session, commit=True, popo=self.dto1)
        fetched = self.dao.fetch_by_order_id(session=self.session, order_id=self.dto1.order_id)
        eq_(len(fetched), 1)
        eq_ignore_certain_fields(fetched[0], self.dto1, ['db_id', 'created_at'])

    def test_fetch_earliest_with_order_id(self):
        self.dao.save(session=self.session, commit=True, popo=self.dto1)
        # dto2 is now the earliest
        self.dto2.processing_time = self.dto1.processing_time - 5000
        self.dao.save(session=self.session, commit=True, popo=self.dto2)
        earliest = self.dao.fetch_earliest_with_order_id(session=self.session, order_id=self.dto2.order_id)
        eq_ignore_certain_fields(earliest, self.dto2, ['db_id', 'created_at'])

    def test_filter_processing_time_greater_than(self):
        self.dao.bulk_save(session=self.session, commit=True, popos=[self.dto1, self.dto2])
        result = self.dao.filter_processing_time_greater_than(session=self.session, processing_time=math.inf)
        eq_(len(result), 0)

        # Assumes dto2.processing_time > dto1.processing_time
        result = self.dao.filter_processing_time_greater_than(session=self.session, processing_time=self.dto1.processing_time)
        eq_(len(result), 2)

        # Assert ordered by processing_time in ascending order
        first = result[0]
        self.dto1.db_id = first.db_id
        self.dto1.created_at = first.created_at
        eq_(first, self.dto1)

        second = result[1]
        self.dto2.db_id = second.db_id
        self.dto2.created_at = second.created_at
        eq_(second, self.dto2)
        assert_greater(second.processing_time, first.processing_time)
