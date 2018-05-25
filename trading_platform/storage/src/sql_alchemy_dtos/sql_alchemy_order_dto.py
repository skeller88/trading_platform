from sqlalchemy import BigInteger, Numeric, Integer, String, Column, Float

from trading_platform.exchanges.src.data.order import Order
from trading_platform.storage.src.sql_alchemy_dtos.base import Base
from trading_platform.utils.src.datetime_operations import utc_timestamp


class SqlAlchemyOrderDto(Base):
    """
    Represents the application record of an order state. The possible lifecycles of an order are (each indentation
    represents a new path, "partially_filled" can recursively generate paths as long as the order is open):

    -> pending
    -> open -> write new entity to table
        -> cancelled
        -> partially_filled
            -> cancelled
            -> partially_filled
            -> filled
        -> filled
    -> failed

    The "orders" table has the following purposes:

    Application (OLTP)
    - Tracking order state. See OrderStatus docstring for possible order states.
    - Update order state in the "orders" OLAP table based on the responses from exchanges on which orders are open. All
    exchanges expose an endpoint to fetch open orders, but not all expose endpoints
    to fetch cancelled orders, closed orders, or even individual orders. So the delta of the state of an order has to be
    derived from the current open orders. See core.market_data.arbitrage_attempt.ArbitrageAttempt for details.
    - Orders that have been filled or cancelled are not removed from this table, because the Order state over time should
        be queryable from an analytics perspective. 

    - ccxt, the exchange library being used, maintains an orders cache: https://github.com/ccxt/ccxt/wiki/Manual#orders-cache
    That cache shouldn't be used because it depends on the application storing the state of the cache in memory. It's
    undesirable to depend on ccxt to manage order state because 1) then ccxt needs to be monitored more closely for
    breaking changes in cache logic, and 2) ccxt's cache implementation does some behind the scenes delta calculation that
    this app should expose in case it's desired to change how order deltas are being tracked.


    Analytics (OLAP)
    - maintain a record of orders placed
    - get orders by event_time
    - get orders by order_status
    """
    __tablename__ = 'orders'
    # primary keys and indexes
    db_id = Column(BigInteger, autoincrement=True, primary_key=True)
    order_index = Column(String, index=True, nullable=False)
    processing_time = Column(Float, index=True, nullable=False)
    exchange_id = Column(Integer, index=True, nullable=False)

    # app metadata
    version = Column(Integer, nullable=False)

    # database metadata
    created_at = Column(Float, default=utc_timestamp, nullable=False)
    updated_at = Column(Float, onupdate=utc_timestamp, nullable=True)

    # exchange-related metadata
    order_id = Column(String, nullable=False)
    order_type = Column(Integer, nullable=True)
    event_time = Column(Float, nullable=True)

    # order numerical data
    amount = Column(Numeric, nullable=True)
    filled = Column(Numeric, nullable=True)
    price = Column(Numeric, nullable=True)
    remaining = Column(Numeric, nullable=True)

    # order metadata
    base = Column(String(15), nullable=False)
    quote = Column(String(15), nullable=False)
    order_status = Column(Integer, nullable=False)
    order_side = Column(Integer, nullable=True)

    def __repr__(self):
        return "<SqlAlchemyOrderDto(db_id='%s', order_index='%s', order_status='%s')>" % (
            self.db_id, self.order_index, self.order_status)

    def to_popo(self):
        params = {
            # app metadata
            'processing_time': self.processing_time,
            'version': self.version,

            # database metadata
            'db_id': self.db_id,
            'order_index': self.order_index,
            'created_at': self.created_at,
            'updated_at': self.updated_at,

            # exchange-related metadata

            'exchange_id': self.exchange_id,
            'event_time': self.event_time,
            'order_id': self.order_id,
            'order_type': self.order_type,

            # order numerical data
            'amount': self.amount,
            'filled': self.filled,
            'price': self.price,
            'remaining': self.remaining,

            # order metadata
            'base': self.base,
            'quote': self.quote,
            'order_status': self.order_status,
            'order_side': self.order_side
        }

        return Order(**params)

    @staticmethod
    def from_popo(popo):
        return SqlAlchemyOrderDto(
            # app metadata
            processing_time=popo.processing_time,
            version=popo.version,

            # database metadata
            db_id=popo.db_id,
            order_index=popo.order_index,
            created_at=popo.created_at,
            updated_at=popo.updated_at,

            # exchange-related metadata

            exchange_id=popo.exchange_id,
            event_time=popo.event_time,
            order_id=popo.order_id,

            # order numerical data
            amount=popo.amount,
            filled=popo.filled,
            price=popo.price,
            remaining=popo.remaining,

            # order metadata
            base=popo.base,
            quote=popo.quote,
            order_status=popo.order_status,
            order_side=popo.order_side,
            order_type=popo.order_type
        )
