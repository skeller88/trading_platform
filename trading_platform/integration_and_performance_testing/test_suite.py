import unittest

from trading_platform.storage.sql_alchemy_engine import SqlAlchemyEngine


class TestIntegrationAndPerformance(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = SqlAlchemyEngine.rds_engine()

    @classmethod
    def setUpClass(cls):
        cls.engine = SqlAlchemyEngine.local_engine_maker()
        cls.engine.initialize_tables()
        cls.session = cls.engine.scoped_session_maker()
        cls.dao = cls.dao_class()
