import traceback
from abc import ABC
from functools import wraps
from typing import Dict, Set, Callable, Optional

from sqlalchemy.orm import Session

from trading_platform.exchanges.data.enums.order_side import OrderSide
from trading_platform.exchanges.data.order import Order
from trading_platform.exchanges.data.pair import Pair
from trading_platform.exchanges.exchange_service_abc import ExchangeServiceAbc
from trading_platform.storage.daos.open_order_dao import OpenOrderDao
from trading_platform.storage.daos.order_dao import OrderDao


class StrategyStateMachineServiceAbc(ABC):
    def __init__(self, state: Dict, logger, exchanges_by_id: Dict[int, ExchangeServiceAbc],
                 open_order_dao: OpenOrderDao, order_dao: OrderDao):
        self.logger = logger
        self.state: Dict = state
        self.exchanges_by_id: Dict[int, ExchangeServiceAbc] = exchanges_by_id
        self.order_dao = order_dao
        self.open_order_dao = open_order_dao

    def next_state(self, next: Optional[Callable] = None, *args, **kwargs):
        current = self.state['current_state']
        self.state[current]['completed'] = True
        next = self.state[current]['success'] if next is None else next
        self.state['current_state'] = next.__name__
        next(*args, **kwargs)

    def place_orders(self, orders: Set[Order], session: Session):
        # if preload_db_state,
        #   insert trade_saga with "pending" status if it doesn't exist
        #   insert orders with "pending" status if they don't exist
        # if preload_exchange_state,
        #   fetch open orders
        #   fetch balance state
        # if async, place orders asynchronously

        # Place orders
        def place_order(order):
            self.logger.info('placing order id {0}'.format(order.order_id))
            exchange = self.exchanges_by_id.get(order.exchange_id)
            pair = Pair(base=order.base, quote=order.quote)

            if order.order_side == OrderSide.buy:
                return exchange.create_limit_buy_order(pair=pair, amount=order.amount, price=order.price)
            else:
                return exchange.create_limit_sell_order(pair=pair, amount=order.amount, price=order.price)

        return map(place_order, orders)

    #     # RDS
    #     begin_trans()
    #     if not sql()
    #         rollback()
    #         retry()
    #     if not commit()
    #         rollback()
    #         retry()
    #     s.new_state(watch_twit)

    # Must occur at the end of the class
    # https://stackoverflow.com/questions/3421337/accessing-a-decorator-in-a-parent-class-from-the-child-in-python


def state(func):
    """
    Decorator method for methods that occur during a state machine.

    Can only be used on class or instance methods because it requires access to self.logger and self.next_state.
    This method also depends on the class implementing the self.failure method.

    Ideally this method would be a method of StateMachineServiceAbc, but I haven't figured out how to do that
    syntax-wise.

    Args:
        func:

    Returns:

    """
    def wrapper():
        # Based on this answer, use @wraps to gain access to self
        # https://stackoverflow.com/questions/11731136/python-class-method-decorator-with-self-arguments
        @wraps(func)
        def wrapped(self, *args, **kwargs):
            try:
                self.logger.debug('start state {0}'.format(func.__name__))
                func(*args, **kwargs)
                self.logger.debug('end state {0}'.format(func.__name__))
                return wrapper
            except Exception:
                self.next_state(self.failure)

        return wrapped