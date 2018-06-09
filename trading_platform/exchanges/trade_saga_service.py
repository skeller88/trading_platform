from typing import Dict

from sqlalchemy.orm import Session

from trading_platform.exchanges.data.trade_saga import TradeSaga
from trading_platform.exchanges.exchange_service_abc import ExchangeServiceAbc
from trading_platform.storage.daos.open_order_dao import OpenOrderDao
from trading_platform.storage.daos.order_dao import OrderDao


class TradeSagaService:
    def __init__(self, exchanges_by_id: Dict[int, ExchangeServiceAbc], open_order_dao: OpenOrderDao, order_dao: OrderDao):
        self.exchanges_by_id: Dict[int, ExchangeServiceAbc] = exchanges_by_id
        self.order_dao = order_dao
        self.open_order_dao = order_dao

    def execute(self, trade_saga: TradeSaga, session: Session):
        def fetch_latest_from_db(order):
            return self.order_dao.fetch_latest_with_order_index(session, order_index=order.order_index)

        orders_from_db = map(fetch_latest_from_db, trade_saga.orders)
