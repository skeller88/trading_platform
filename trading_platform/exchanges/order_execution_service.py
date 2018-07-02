from concurrent.futures import ThreadPoolExecutor
from logging import Logger
from time import sleep
from typing import Dict, Set, Iterable

from sqlalchemy.orm import Session, scoped_session

from trading_platform.exchanges.data.enums.order_side import OrderSide
from trading_platform.exchanges.data.enums.order_status import OrderStatus
from trading_platform.exchanges.data.order import Order
from trading_platform.exchanges.data.pair import Pair
from trading_platform.exchanges.exchange_service_abc import ExchangeServiceAbc
from trading_platform.storage.daos.order_dao import OrderDao


class OrderExecutionService:
    def __init__(self, **kwargs):
        self.logger: Logger = kwargs.get('logger')
        self.exchanges_by_id: Dict[id, ExchangeServiceAbc] = kwargs.get('exchanges_by_id')
        self.order_dao: OrderDao = kwargs.get('order_dao')
        self.multithreaded: bool = kwargs.get('multithreaded')
        self.num_order_status_checks = kwargs.get('num_order_status_checks', 3)
        self.scoped_session_maker: scoped_session = kwargs.get('scoped_session_maker')
        self.sleep_time_sec_between_order_checks = kwargs.get('sleep_time_sec_between_order_checks', 4)

        if self.multithreaded:
            self.thread_pool_executer: ThreadPoolExecutor = ThreadPoolExecutor(max_workers=10)

    def execute_order_set(self, orders: Set[Order], write_pending_order: bool,
                          check_if_orders_filled: bool) -> Dict[str, Order]:
        def execute_order_with_session(order) -> Order:
            return self.execute_order(order, self.scoped_session_maker(), write_pending_order, check_if_order_filled=check_if_orders_filled)

        order_execution_attempts: Iterable[Order] = map(execute_order_with_session, orders)
        executed_orders: Iterable[Order] = filter(lambda order: order is not None, order_execution_attempts)
        order_dict = {order.order_id: order for order in executed_orders}
        return order_dict

    def execute_order(self, order: Order, session: Session, write_pending_order: bool,
                      check_if_order_filled: bool) -> Order:
        """

        Args:
            order:
            session:
            write_pending_order:
            check_if_order_filled:

        Returns: Order. order_status == OrderStatus.filled if order was filled, else OrderStatus.open

        """
        self.logger.info('executing order with order_id {0} on exchange {1} on order_side {2}'.format(
            order.order_id,
            order.exchange_id,
            order.order_side))

        exchange = self.exchanges_by_id.get(order.exchange_id)
        exchange_method = exchange.create_limit_buy_order if order.order_side == OrderSide.buy else exchange.create_limit_sell_order

        try:
            if write_pending_order:
                order.order_status = OrderStatus.pending
                self.order_dao.save(popo=order, session=session, commit=True)

            order_snapshot: Order = exchange_method(order, params=order.params)

            self.save_order(order_snapshot, session)

            if check_if_order_filled:
                return self.poll_exchange_for_order_status(OrderStatus.filled, session, order_snapshot)

            return order_snapshot
        except Exception as ex:
            self.logger.error(ex)
            raise ex

    def poll_exchange_for_order_status(self, order_status: OrderStatus.filled, session: Session, order: Order) -> Order:
        """
        Args:
            session:
            order_status:
            order:

        Returns: Order. The filled order from the exchange, or the latest order snapshot, whose
            order_status will be either "open" or "partially_filled".

        """
        order_snapshot: Order = order
        exchange: ExchangeServiceAbc = self.exchanges_by_id.get(order.exchange_id)
        for attempt in range(self.num_order_status_checks):
            order_snapshot: Order = exchange.fetch_order(order.exchange_order_id,
                                                         pair=Pair(base=order.base, quote=order.quote))
            if order_snapshot is not None and order_snapshot.order_status == order_status:
                self.save_order(order_snapshot, session)
                return order_snapshot

            sleep(self.sleep_time_sec_between_order_checks)

        return order_snapshot

    def save_order(self, order: Order, session: Session):
        if self.multithreaded:
            self.thread_pool_executer.submit(self.order_dao.save, popo=order, session=session, commit=True)
        else:
            self.order_dao.save(popo=order, session=session, commit=True)

    def update_order(self, order: Order, session: Session):
        """
        TODO - this method isn't necessary yet, but implement it.

        Cancel the previously order placed with a new order. Assumes that updated_order has already been placed.

        Args:
            order:
            session:

        Returns:

        """
        self.logger.info('updating order')

        exchange = self.exchanges_by_id.get(order.exchange_id)
        exchange_method = exchange.create_limit_buy_order if order.order_side == OrderSide.buy else exchange.create_limit_sell_order

        order: Order = exchange.fetch_order(exchange_order_id=order.exchange_order_id,
                                            symbol=self.pair.name_for_exchange_clients)
        # TODO will order_status ever == filled?
        if order.order_status == OrderStatus.filled:
            self.logger.info('sell order filled - exchange_exchange_order_id - {0}'.format(
                self.sell_order.exchange_exchange_order_id))
            self.new_market_execution.sell_order_executed = True
            return self.new_market_execution

        self.logger.info('cancelling sell order - exchange_exchange_order_id - {0}'.format(
            self.sell_order.exchange_exchange_order_id))

        # TODO use cancelled attributes?
        cancelled: Order = self.bittrex.cancel_order()
        self.sell_order = None
        self.new_market_execution.sell_exchange_order_id = None
        # TODO account for when order is partially filled at the moment it's cancelled
        self.order_dao.update(db_id=self.sell_order.db_id, update_dict={
            'order_status': cancelled.order_status
        }, session=session, commit=True)
        sleep(self.sleep_for_exchange_consistency_sec)
        self.logger.info('replacing sell order')
        self.execute_order(order, session, False, False)

    def cancel_order(self, order: Order):
        pass
        # cancel order

        # use order_dao to write a new cancelled order

        # if there's an error cancelling the order because the order doesn't exist, then figure out the actual
        # status of the order and record in the database
