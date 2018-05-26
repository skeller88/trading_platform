from sqlalchemy import and_, inspect

from trading_platform.storage.decorators.sessions import with_write_session, with_read_session
from trading_platform.storage.sql_alchemy_dtos.sql_alchemy_ticker_dto import SqlAlchemyTickerDto


class TickerDaoWithDecorators:
    """
    This class doesn't work yet.

    Wrapper class of whatever ORM or SQL framework is used. Capabilities of this class:
    - translating the Python object to and from a DAO object
    - CRUD operations
    - creating sessions or using an existing session
    - committing or flushing a session to the database

    The inner() method of these methods performs the database operation. Additional logic outside of the the inner()
    is needed to convert the dao to a POPO (plain old python object). Why convert to a POPO? Because then the database
    logic bound to the DAO is decoupled from the application logic. If in the future the database logic needs to be
    changed dramatically, the application logic shouldn't be aware of that. This is especially important when creating or
    updating an entity to ensure that the dao reflects the post-commit/post-flush state of the entity in the database.
    For example, until a new entity is committed to the database, its dao.db_id is None. Don't convert from a dao to a POPO until after database
    operations are complete.
    """
    def __init__(self, dao_class=SqlAlchemyTickerDto):
        self.dao_class = dao_class

    # Create
    def save(self, session, flush=False, commit=False, ticker=None):
        @with_write_session(session=session, flush=flush, commit=commit)
        def inner():
            ticker_dao = self.dao_class.from_popo(ticker)
            session.add(ticker_dao)
            return ticker_dao

        session, ticker_dao = inner()
        return session, ticker_dao.to_popo()

    def bulk_save(self, session, flush=False, commit=False, tickers=None):
        @with_write_session(session=session, flush=flush, commit=commit)
        def inner():
            ticker_daos = [self.dao_class.from_popo(ticker) for ticker in tickers]

            for ticker_dao in ticker_daos:
                session.add(ticker_dao)

            return ticker_daos

        session, ticker_daos = inner()
        saved_tickers = [self.dao_class.to_popo(ticker_dao) for ticker_dao in ticker_daos]

        session.close()
        return session, saved_tickers

    # Read
    def fetch_by_db_id(self, session, db_id):
        @with_read_session(session=session)
        def inner():
            return session.query(SqlAlchemyTickerDto).filter_by(db_id=db_id).first()

        session, ticker_dao = inner()

        if ticker_dao is not None:
            return session, ticker_dao.to_popo()

        return session, None

    def fetch_by_event_time_between_range(self, session, start, end):
        @with_read_session(session=session)
        def inner():
            return session.query(SqlAlchemyTickerDto).filter(and_(SqlAlchemyTickerDto.event_time >= start,
                                                                  SqlAlchemyTickerDto.event_time < end)).all()

        session, ticker_daos = inner()
        print(ticker_daos)
        tickers = [ticker_dao.to_popo() for ticker_dao in ticker_daos]

        return session, tickers

    def fetch_by_event_time_gte_range(self, session, start):
        @with_read_session(session=session)
        def inner():
            return session.query(SqlAlchemyTickerDto).filter(SqlAlchemyTickerDto.event_time >= start).all()

        session, ticker_daos = inner()
        tickers = [ticker_dao.to_popo() for ticker_dao in ticker_daos]

        return session, tickers

    # Delete
    def delete_all(self, session, flush=False, commit=False):
        @with_write_session(session=session, flush=flush, commit=commit)
        def inner():
            return session.query(SqlAlchemyTickerDto).delete()

        return inner()
