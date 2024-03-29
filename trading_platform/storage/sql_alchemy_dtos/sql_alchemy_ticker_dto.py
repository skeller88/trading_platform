from sqlalchemy import BigInteger, Column, Numeric, Integer, String, Float, DECIMAL

from trading_platform.exchanges.data.financial_data import FinancialData
from trading_platform.exchanges.data.ticker import Ticker
from trading_platform.storage.sql_alchemy_dtos.base import Base
from trading_platform.utils.datetime_operations import utc_timestamp


class SqlAlchemyTickerDto(Base):
    __tablename__ = 'tickers'
    db_id = Column(BigInteger, autoincrement=True, primary_key=True)
    app_create_timestamp = Column(Float, index=True, nullable=False)
    exchange_id = Column(Integer, index=True, nullable=False)

    base = Column(String(15), index=True, nullable=False)
    quote = Column(String(15), index=True, nullable=False)

    ask = Column(DECIMAL(scale=FinancialData.eight_places), nullable=False)
    bid = Column(DECIMAL(scale=FinancialData.eight_places), nullable=False)
    base_volume = Column(DECIMAL(scale=FinancialData.eight_places), nullable=True)
    quote_volume = Column(DECIMAL(scale=FinancialData.eight_places), nullable=True)

    db_create_timestamp = Column(Float, default=utc_timestamp, nullable=False)
    db_update_timestamp = Column(Float, onupdate=utc_timestamp, nullable=True)
    last = Column(Numeric, nullable=False)

    exchange_timestamp = Column(Float, nullable=True)
    version = Column(Integer, nullable=False)

    def __repr__(self):
        return "<SqlAlchemyTickerDto(db_id='%s', app_create_timestamp='%s', quote='%s', base='%s')>" % (self.db_id,
                                                                                                        self.app_create_timestamp,
                                                                                                        self.quote,
                                                                                                        self.base)

    def to_popo(self):
        kwargs = {
            'ask': self.ask,
            'bid': self.bid,
            'base_volume': self.base_volume,
            'quote_volume': self.quote_volume,
            'base': self.base.strip(),
            'exchange_id': self.exchange_id,
            'exchange_timestamp': self.exchange_timestamp,
            'last': self.last,
            'quote': self.quote.strip(),
            'db_id': self.db_id,
            'app_create_timestamp': self.app_create_timestamp,
            'version': self.version
        }
        return Ticker(**kwargs)

    @staticmethod
    def from_popo(popo):
        return SqlAlchemyTickerDto(ask=popo.ask, base=popo.base, bid=popo.bid,
                                   base_volume=popo.base_volume, quote_volume=popo.quote_volume,
                                   exchange_id=popo.exchange_id,
                                   exchange_timestamp=popo.exchange_timestamp, last=popo.last,
                                   db_create_timestamp=popo.db_create_timestamp,
                                   db_update_timestamp=popo.db_update_timestamp,
                                   app_create_timestamp=popo.app_create_timestamp, quote=popo.quote,
                                   db_id=popo.db_id, version=popo.version)
