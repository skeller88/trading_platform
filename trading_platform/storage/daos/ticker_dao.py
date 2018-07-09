from sqlalchemy import and_

from trading_platform.storage.daos.dao import Dao
from trading_platform.storage.sql_alchemy_dtos.sql_alchemy_ticker_dto import SqlAlchemyTickerDto


class TickerDao(Dao):
    def __init__(self):
        super().__init__(dto_class=SqlAlchemyTickerDto)

    def fetch_by_exchange_timestamp_between_range(self, session, start, end):
        try:
            ticker_daos = session.query(SqlAlchemyTickerDto).filter(and_(SqlAlchemyTickerDto.exchange_timestamp >= start,
                                                                         SqlAlchemyTickerDto.exchange_timestamp < end)).all()
            tickers = [ticker_dao.to_popo() for ticker_dao in ticker_daos]

            return tickers
        except Exception as exception:
            print('rolling back due to exception')
            session.rollback()
            raise exception

    def fetch_by_exchange_timestamp_gte_range(self, session, start):
        try:
            ticker_daos = session.query(SqlAlchemyTickerDto).filter(SqlAlchemyTickerDto.exchange_timestamp >= start).all()
            tickers = [ticker_dao.to_popo() for ticker_dao in ticker_daos]

            return tickers
        except Exception as exception:
            print('rolling back due to exception')
            session.rollback()
            raise exception
