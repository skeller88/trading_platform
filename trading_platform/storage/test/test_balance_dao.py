"""
nosetests test.storage.test_balance_dao --nocapture
"""
import unittest
from copy import deepcopy

import sqlalchemy
from nose.tools import assert_true, eq_, assert_raises

from trading_platform.exchanges.src.data.balance import Balance
from trading_platform.exchanges.src.data.enums import exchange_ids
from trading_platform.storage.src.daos.balance_dao import BalanceDao
from trading_platform.storage.src.sql_alchemy_engine import SqlAlchemyEngine
from trading_platform.utils.src.datetime_operations import utc_timestamp
from trading_platform.core.test import data

SECONDS_PER_MIN = 60
SECONDS_PER_DAY = SECONDS_PER_MIN*60*24
TICKER_VERSION = 0


class TestBalanceDao(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = SqlAlchemyEngine.local_engine_maker()
        cls.engine.initialize_tables()
        cls.session = cls.engine.scoped_session_maker()
        cls.dao = BalanceDao()
        cls.popo_class = Balance

    def setUp(self):
        self.dto1 = data.balance(exchange_ids.binance)
        self.dto2 = data.balance(exchange_ids.bittrex)

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

    def test_fetch_all(self):
        session, fetched = self.dao.fetch_all(self.session)
        eq_(len(fetched), 0)
        session, created = self.dao.bulk_save(session=self.session, commit=True,
                                                     popos=[self.dto1, self.dto2])
        session, fetched = self.dao.fetch_all(self.session)
        eq_(len(fetched), 2)

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

    def test_delete_all(self):
        session, created = self.dao.bulk_save(session=self.session, commit=True,
                                                     popos=[self.dto1, self.dto2])
        eq_(len(created), 2)
        session, deleted = self.dao.delete_all(session=self.session, commit=True)
        eq_(deleted, 2)