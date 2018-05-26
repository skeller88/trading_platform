from sqlalchemy import BigInteger, Column, Numeric, Integer, String, Float, DECIMAL

from trading_platform.exchanges.data.financial_data import FinancialData
from trading_platform.exchanges.data.ticker import Ticker
from trading_platform.storage.sql_alchemy_dtos.base import Base
from trading_platform.utils.datetime_operations import utc_timestamp


class SqlAlchemyTickerDto(Base):
    __tablename__ = 'tickers'
    db_id = Column(BigInteger, autoincrement=True, primary_key=True)
    processing_time = Column(Float, index=True, nullable=False)
    exchange_id = Column(Integer, index=True, nullable=False)
    base = Column(String(15), index=True, nullable=False)
    quote = Column(String(15), index=True, nullable=False)

    ask = Column(DECIMAL(scale=FinancialData.decimal_scale), nullable=False)
    bid = Column(DECIMAL(scale=FinancialData.decimal_scale), nullable=False)
    created_at = Column(Float, default=utc_timestamp, nullable=False)
    last = Column(Numeric, nullable=False)

    event_time = Column(Float, nullable=False)
    updated_at = Column(Float, onupdate=utc_timestamp, nullable=True)
    version = Column(Integer, nullable=False)

    def __repr__(self):
        return "<SqlAlchemyTickerDto(db_id='%s', processing_time='%s', quote='%s', base='%s')>" % (self.db_id,
                                                                                             self.processing_time,
                                                                                             self.quote, self.base)

    def to_popo(self):
        kwargs = {
            'ask':self.ask,
            'bid':self.bid,
            'base':self.base.strip(),
            'exchange_id':self.exchange_id,
            'event_time':self.event_time,
            'last':self.last,
            'quote':self.quote.strip(),
            'db_id':self.db_id,
            'processing_time':self.processing_time,
            'version':self.version
        }
        return Ticker(**kwargs)

    @staticmethod
    def from_popo(popo):
        return SqlAlchemyTickerDto(ask=popo.ask, base=popo.base, bid=popo.bid, exchange_id=popo.exchange_id,
                                   event_time=popo.event_time, last=popo.last,
                                   processing_time=popo.processing_time, quote=popo.quote,
                                   db_id=popo.db_id, version=popo.version)

