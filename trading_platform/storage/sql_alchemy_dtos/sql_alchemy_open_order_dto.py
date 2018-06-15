from sqlalchemy import BigInteger, Numeric, Integer, String, Column, Float

from trading_platform.exchanges.data.order import Order
from trading_platform.storage.sql_alchemy_dtos.base import Base
from trading_platform.utils.datetime_operations import utc_timestamp


class SqlAlchemyOpenOrderDto(Base):
    """
    # TODO - consolidate this docstring with Order docstring.

    Represents the application record of an open order state. Same as the SqlAlchemyOrderDto, but without the 
    numerical fields. See the Order docstring for more information about an Order.

    The "open_orders" table is used at the Application layer only. It has the following purposes:

    Application (OLTP)
    - allow for fetch_open_orders() calls by pair symbol. On Binance, fetching open orders without specifying a symbol 
        is rate-limited to one call per 152 seconds. At the app layer, a list of open orders is returned, and a 
        fetch_open_orders() call is made for the symbol derived from the base and quote of each order. 
    - see core/storage/sql_alchemy_dtos/sql_alchemy_arbitrage_attempt_dto.py docstring for details.
    - Track which orders are open, and remove orders that have been filled or cancelled.
    - Update order state in the "orders" OLAP table based on the responses from exchanges on which orders are open. All
    exchanges expose an endpoint to fetch open orders, but not all expose endpoints
    to fetch cancelled orders or closed orders. So the delta of the state of an order has to be
    derived from the current open orders. See core.market_data.arbitrage_attempt.ArbitrageAttempt for details.

    - ccxt, the exchange library being used, maintains an orders cache: https://github.com/ccxt/ccxt/wiki/Manual#orders-cache
    That cache shouldn't be used because it depends on the application storing the state of the cache in memory. It's
    undesirable to depend on ccxt to manage order state because 1) then ccxt needs to be monitored more closely for
    breaking changes in cache logic, and 2) ccxt's cache implementation does some behind the scenes delta calculation that
    this app should expose in case it's desired to change how order deltas are being tracked.
    """
    __tablename__ = 'open_orders'
    # primary keys and indexes
    db_id = Column(BigInteger, autoincrement=True, primary_key=True)
    order_id = Column(String, index=True, nullable=False)
    processing_time = Column(Float, index=True, nullable=False)
    exchange_id = Column(Integer, index=True, nullable=False)

    # app metadata
    version = Column(Integer, nullable=False)

    # database metadata
    created_at = Column(Float, default=utc_timestamp, nullable=False)
    updated_at = Column(Float, onupdate=utc_timestamp, nullable=True)

    # exchange-related metadata
    exchange_order_id = Column(String, nullable=False)
    order_type = Column(Integer, nullable=True)
    event_time = Column(Float, nullable=True)

    # order metadata
    base = Column(String(15), nullable=False)
    quote = Column(String(15), nullable=False)
    order_status = Column(Integer, nullable=False)
    order_side = Column(Integer, nullable=True)

    def __repr__(self):
        return "<SqlAlchemyOpenOrderDto(db_id='%s', order_id='%s', order_status='%s')>" % (
            self.db_id, self.order_id, self.order_status)

    def to_popo(self):
        params = {
            # app metadata
            'processing_time': self.processing_time,
            'version': self.version,

            # database metadata
            'db_id': self.db_id,
            'order_id': self.order_id,
            'created_at': self.created_at,
            'updated_at': self.updated_at,

            # exchange-related metadata

            'exchange_id': self.exchange_id,
            'event_time': self.event_time,
            'exchange_order_id': self.exchange_order_id,
            'order_type': self.order_type,

            # order metadata
            'base': self.base,
            'quote': self.quote,
            'order_status': self.order_status,
            'order_side': self.order_side
        }

        return Order(**params)

    @staticmethod
    def from_popo(popo):
        return SqlAlchemyOpenOrderDto(
            # app metadata
            processing_time=popo.processing_time,
            version=popo.version,

            # database metadata
            db_id=popo.db_id,
            order_id=popo.order_id,
            created_at=popo.created_at,
            updated_at=popo.updated_at,

            # exchange-related metadata

            exchange_id=popo.exchange_id,
            event_time=popo.event_time,
            exchange_order_id=popo.exchange_order_id,

            # order metadata
            base=popo.base,
            quote=popo.quote,
            order_status=popo.order_status,
            order_side=popo.order_side,
            order_type=popo.order_type
        )
