from sqlalchemy import and_, inspect

from storage.src.daos.dao import Dao
from storage.src.decorators.sessions import with_write_session, with_read_session
from storage.src.sql_alchemy_dtos.sql_alchemy_ticker_dto import SqlAlchemyTickerDto


class TickerDao(Dao):
    def __init__(self):
        super().__init__(dto_class=SqlAlchemyTickerDto)

    def fetch_by_event_time_between_range(self, session, start, end):
        try:
            ticker_daos = session.query(SqlAlchemyTickerDto).filter(and_(SqlAlchemyTickerDto.event_time >= start,
                                                                         SqlAlchemyTickerDto.event_time < end)).all()
            tickers = [ticker_dao.to_popo() for ticker_dao in ticker_daos]

            return session, tickers
        except Exception as exception:
            print('rolling back due to exception')
            session.rollback()
            raise exception

    def fetch_by_event_time_gte_range(self, session, start):
        try:
            ticker_daos = session.query(SqlAlchemyTickerDto).filter(SqlAlchemyTickerDto.event_time >= start).all()
            tickers = [ticker_dao.to_popo() for ticker_dao in ticker_daos]

            return session, tickers
        except Exception as exception:
            print('rolling back due to exception')
            session.rollback()
            raise exception

    # Delete
    def delete_all(self, session, flush=False, commit=False):
        try:
            deleted_count = session.query(SqlAlchemyTickerDto).delete()

            if flush:
                session.flush()
            if commit:
                session.commit()

            return session, deleted_count
        except Exception as exception:
            print('rolling back due to exception')
            session.rollback()
            raise exception
