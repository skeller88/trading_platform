from concurrent.futures import ThreadPoolExecutor
from logging import Logger
from typing import Dict, Set, Iterable

from sqlalchemy.orm import Session

from trading_platform.exchanges.data.enums.order_side import OrderSide
from trading_platform.exchanges.data.enums.order_status import OrderStatus
from trading_platform.exchanges.data.order import Order
from trading_platform.exchanges.exchange_service_abc import ExchangeServiceAbc
from trading_platform.storage.daos.order_dao import OrderDao


class OrderExecutionService:
    def __init__(self, logger: Logger, order_dao: OrderDao, exchanges_by_id: Dict[id, ExchangeServiceAbc],
                 multithreaded: bool):
        self.logger = logger
        self.exchanges_by_id = exchanges_by_id
        self.order_dao = order_dao
        self.multithreaded = multithreaded

        if multithreaded:
            self.thread_pool_executer = ThreadPoolExecutor(max_workers=10)

    def execute_order_set(self, orders: Set[Order], session: Session, write_pending_order: bool) -> Dict[str, Order]:
        def execute_order_with_session(order) -> Order:
            return self.execute_order(order, session, write_pending_order)

        order_execution_attempts: Iterable[Order] = map(execute_order_with_session, orders)
        executed_orders: Iterable[Order] = filter(lambda order: order is not None, order_execution_attempts)
        order_dict = {order.order_id: order for order in executed_orders}
        return order_dict

    def execute_order(self, order: Order, session: Session, write_pending_order: bool) -> Order:
        exchange = self.exchanges_by_id.get(order.exchange_id)

        self.logger.info('executing order with exchange_order_id {0} on exchange {1} on order_side {2}'.format(
            order.exchange_order_id,
            order.exchange_id,
            order.order_side))

        exchange_method_name = 'create_limit_buy_order' if order.order_side == OrderSide.buy else 'create_limit_sell_order'
        exchange_method = getattr(exchange, exchange_method_name)

        try:
            if write_pending_order:
                order.order_status = OrderStatus.pending
                self.order_dao.save(popo=order, session=session, commit=True)

            executed_order: Order = exchange_method(order, params=order.params)

            # TODO - make sure the exchange_method returns the strategy_id field for the executed Order

            if self.multithreaded:
                self.thread_pool_executer.submit(self.order_dao.save, popo=executed_order, session=session, commit=True)
            else:
                self.order_dao.save(popo=executed_order, session=session, commit=True)

            return executed_order
        except Exception as ex:
            self.logger.error(ex)

    def cancel_order(self, order: Order):
        pass
        # cancel order

        # use order_dao to write a new cancelled order

        # if there's an error cancelling the order because the order doesn't exist, then figure out the actual
        # status of the order and record in the database
