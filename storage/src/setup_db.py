from storage.src.sql_alchemy_engine import SqlAlchemyEngine


def setup_local_sql_alchemy():
    engine = SqlAlchemyEngine.local_engine_maker()
    engine.initialize_tables()
    return engine


def setup_remote_sql_alchemy():
    engine = SqlAlchemyEngine.rds_engine()
    engine.initialize_tables()
    return engine