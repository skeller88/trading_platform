import pytest

from trading_platform.storage.sql_alchemy_engine import SqlAlchemyEngine


@pytest.mark.usefixtures('engine')
class TestSqlAlchemyEngine:
    @pytest.fixture(scope='function')
    def engine(self, request):
        engine_instance = SqlAlchemyEngine.rds_engine()

        def tearDown():
            engine_instance.dispose()

        request.addfinalizer(tearDown)

        return engine_instance

    def test_connect(self, engine):
        """
        Should connect to the database
        Args:
            engine:

        Returns:

        """
        assert(engine is not None)

    def test_connect_and_update_tables(self, engine):
        """
        Should be able to update tables.
        Args:
            engine:

        Returns:

        """
        engine.update_tables()
