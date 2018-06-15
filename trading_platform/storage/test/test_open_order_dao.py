"""
nosetests test.storage.test_order_dao --nocapture
"""
import unittest
from copy import deepcopy, copy

import math
import sqlalchemy
from nose.tools import assert_true, eq_, assert_raises, assert_greater

from trading_platform.core.test import data
from trading_platform.exchanges.data.order import Order
from trading_platform.storage.daos.open_order_dao import OpenOrderDao
from trading_platform.exchanges.data.enums import exchange_ids
from trading_platform.storage.sql_alchemy_engine import SqlAlchemyEngine
from trading_platform.utils.datetime_operations import utc_timestamp

SECONDS_PER_MIN = 60
SECONDS_PER_DAY = SECONDS_PER_MIN * 60 * 24
TICKER_VERSION = 0


class TestOpenOrderDao(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = SqlAlchemyEngine.local_engine_maker()
        cls.engine.initialize_tables()
        cls.session = cls.engine.scoped_session_maker()
        cls.dao = OpenOrderDao()
        cls.popo_class = Order

    def setUp(self):
        self.dto1 = data.order(exchange_ids.binance, numerical_fields=False)
        self.dto2 = data.order(exchange_ids.bittrex, processing_time=self.dto1.processing_time + 5000.,
                               numerical_fields=False)

    def tearDown(self):
        self.dao.delete_all(session=self.session)
        self.session.commit()
        self.session.close_all()

    @classmethod
    def tearDownClass(cls):
        cls.engine.drop_tables()

    # Create
    def test_save_and_commit(self):
        session, created = self.dao.save(session=self.session, commit=True, popo=self.dto1)
        assert_true(created.db_id)
        assert_true(created.processing_time)
        self.dto1.created_at = created.created_at
        self.dto1.db_id = created.db_id
        eq_(created, self.dto1)

    def test_save_with_nullable_fields_no_constraint_violation_(self):
        for field in self.popo_class.nullable_fields:
            dto = deepcopy(self.dto1)
            setattr(dto, field, None)
            self.dao.save(session=self.session, commit=True, popo=dto)

    def test_save_with_required_fields_raises_constraint_violation_(self):
        for field in self.popo_class.required_fields:
            dto = deepcopy(self.dto1)
            setattr(dto, field, None)
            assert_raises(sqlalchemy.exc.ProgrammingError, session=self.session, commit=True, popo=dto)

    def test_bulk_save_and_commit(self):
        session, created = self.dao.bulk_save(session=self.session, commit=True, popos=[self.dto1, self.dto2])
        eq_(len(created), 2)

        for dto in created:
            assert_true(dto.db_id)
            assert_true(dto.event_time)
            assert_true(dto.processing_time)

    # Read
    def test_fetch_by_id(self):
        session, created = self.dao.save(session=self.session, commit=True, popo=self.dto1)
        session, fetched = self.dao.fetch_by_db_id(self.session, created.db_id)
        eq_(fetched, created)

    def test_fetch_by_nonexistent_id(self):
        session, fetched = self.dao.fetch_by_db_id(self.session, int(utc_timestamp()))
        eq_(fetched, None)

    def test_filter_processing_time_greater_than(self):
        self.dao.bulk_save(session=self.session, commit=True, popos=[self.dto1, self.dto2])
        result = self.dao.filter_processing_time_greater_than(session=self.session, processing_time=math.inf)
        eq_(len(result), 0)

        # Assumes dto2.processing_time > dto1.processing_time
        result = self.dao.filter_processing_time_greater_than(session=self.session,
                                                              processing_time=self.dto1.processing_time)
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

    # Delete
    def test_delete(self):
        session, created = self.dao.bulk_save(session=self.session, commit=True,
                                              popos=[self.dto1, self.dto2])
        eq_(len(created), 2)
        to_delete_db_id = created[0].db_id
        session, deleted = self.dao.delete(session=self.session, db_id=to_delete_db_id, commit=True)
        eq_(deleted, 1)
        session, deleted = self.dao.fetch_by_db_id(self.session, to_delete_db_id)
        eq_(deleted, None)

    def test_bulk_delete_by_order_id(self):
        dto3 = copy(self.dto1)
        self.dao.bulk_save(session=self.session, commit=True,
                           popos=[self.dto1, self.dto2, dto3])
        self.dao.bulk_delete_by_order_id(session=self.session, commit=True, popos=[self.dto1])

        # dto1 and dto3 have the same order_id, so they both should be deleted
        session, fetched = self.dao.fetch_all(self.session)
        eq_(len(fetched), 1)

        self.dao.save(session=self.session, commit=True, popo=self.dto1)
        self.dao.bulk_delete_by_order_id(session=self.session, commit=True,
                                            popos=[self.dto1, self.dto2])

        # all dtos should be deleted
        session, fetched = self.dao.fetch_all(self.session)
        eq_(len(fetched), 0)

    def test_delete_all(self):
        session, created = self.dao.bulk_save(session=self.session, commit=True,
                                              popos=[self.dto1, self.dto2])
        eq_(len(created), 2)
        session, deleted = self.dao.delete_all(session=self.session, commit=True)
        eq_(deleted, 2)
