from sqlalchemy import BigInteger, Column, Numeric, Integer, String, Float

from trading_platform.exchanges.data.balance import Balance
from trading_platform.storage.sql_alchemy_dtos.base import Base
from trading_platform.utils.datetime_operations import utc_timestamp


class SqlAlchemyBalanceDto(Base):
    __tablename__ = 'balances'
    db_id = Column(BigInteger, autoincrement=True, primary_key=True)
    # get balance by currency
    currency = Column(String(15), index=True, nullable=False)
    # get balance by processing time
    processing_time = Column(Float, index=True, nullable=False)
    # get balance by exchange
    exchange_id = Column(Integer, index=True, nullable=False)

    free = Column(Numeric, nullable=False)
    locked = Column(Numeric, nullable=False)
    total = Column(Numeric, nullable=False)

    event_time = Column(Float, nullable=True)

    created_at = Column(Float, default=utc_timestamp, nullable=False)
    updated_at = Column(Float, onupdate=utc_timestamp, nullable=True)
    version = Column(Integer, nullable=False)

    def __repr__(self):
        return "<SqlAlchemyBalanceDto(db_id='%s', processing_time='%s', currency='%s', exchange_id='%s')>" % (
            self.db_id, self.processing_time, self.currency, self.exchange_id)

    def to_popo(self):
        kwargs = {
            'db_id': self.db_id,
            'created_at': self.created_at,
            'updated_at': self.updated_at,

            'currency': self.currency.strip(),
            'exchange_id': self.exchange_id,

            'free': self.free,
            'locked': self.locked,
            'total': self.total,

            'version': self.version,
            'event_time': self.event_time,
            'processing_time': self.processing_time,
        }

        return Balance(**kwargs)

    @staticmethod
    def from_popo(popo):
        return SqlAlchemyBalanceDto(currency=popo.currency.strip(), exchange_id=popo.exchange_id, free=popo.free,
                                    locked=popo.locked,
                                    total=popo.total, event_time=popo.event_time, processing_time=popo.processing_time,
                                    db_id=popo.db_id, version=popo.version)
