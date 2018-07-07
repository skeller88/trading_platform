"""
nosetests test.storage.test_balance_dao --nocapture
"""
import unittest
from copy import deepcopy

import sqlalchemy
from nose.tools import assert_true, eq_, assert_raises

from trading_platform.storage.sql_alchemy_engine import SqlAlchemyEngine
from trading_platform.utils.datetime_operations import utc_timestamp


class TestDao(unittest.TestCase):
    """
    To subclass, set __test__ = True and in the setUp() method, define self.dto1 and self.dto2.
    """
    __test__ = False  # important, makes sure tests are not run on base class
    # Each inheritor of this class will set these values
    dao_class = None
    popo_class = None

    @classmethod
    def setUpClass(cls):
        cls.engine = SqlAlchemyEngine.local_engine_maker()
        cls.engine.initialize_tables()
        cls.session = cls.engine.scoped_session_maker()
        cls.dao = cls.dao_class()

    def tearDown(self):
        self.dao.delete_all(session=self.session)
        self.session.commit()
        self.session.close_all()

    @classmethod
    def tearDownClass(cls):
        cls.engine.drop_tables()

    # Create
    def test_save_and_commit(self):
        created = self.dao.save(session=self.session, commit=True, popo=self.dto1)
        assert_true(created.db_id)
        assert_true(created.app_create_timestamp)
        self.dto1.db_create_timestamp = created.db_create_timestamp
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
        created = self.dao.bulk_save(session=self.session, commit=True, popos=[self.dto1, self.dto2])
        eq_(len(created), 2)

        for dto in created:
            for field in self.popo_class.required_fields:
                assert(getattr(dto, field) is not None)

    # Read
    def test_fetch_by_id(self):
        created = self.dao.save(session=self.session, commit=True, popo=self.dto1)
        fetched = self.dao.fetch_by_db_id(db_id=created.db_id, session=self.session)
        eq_(fetched, created)

    def test_fetch_by_nonexistent_id(self):
        fetched = self.dao.fetch_by_db_id(self.session, int(utc_timestamp()))
        eq_(fetched, None)

    def test_fetch_all(self):
        fetched = self.dao.fetch_all(self.session)
        eq_(len(fetched), 0)
        created = self.dao.bulk_save(session=self.session, commit=True,
                                                     popos=[self.dto1, self.dto2])
        fetched = self.dao.fetch_all(self.session)
        eq_(len(fetched), 2)

    # Delete
    def test_delete(self):
        created = self.dao.bulk_save(session=self.session, commit=True,
                                                     popos=[self.dto1, self.dto2])
        eq_(len(created), 2)
        to_delete_db_id = created[0].db_id
        deleted = self.dao.delete(session=self.session, db_id=to_delete_db_id, commit=True)
        eq_(deleted, 1)
        deleted = self.dao.fetch_by_db_id(self.session, to_delete_db_id)
        eq_(deleted, None)

    def test_delete_all(self):
        created = self.dao.bulk_save(session=self.session, commit=True,
                                                     popos=[self.dto1, self.dto2])
        eq_(len(created), 2)
        deleted = self.dao.delete_all(session=self.session, commit=True)
        eq_(deleted, 2)