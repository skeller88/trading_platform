from abc import ABC
from typing import Dict, Set

from sqlalchemy.orm import Session

from trading_platform.exchanges.data.enums.order_side import OrderSide
from trading_platform.exchanges.data.order import Order
from trading_platform.exchanges.data.pair import Pair
from trading_platform.exchanges.exchange_service_abc import ExchangeServiceAbc
from trading_platform.storage.daos.open_order_dao import OpenOrderDao
from trading_platform.storage.daos.order_dao import OrderDao


class StrategyStateMachineServiceAbc(ABC):
    def __init__(self, state_machine: Dict, logger, exchanges_by_id: Dict[int, ExchangeServiceAbc],
                 open_order_dao: OpenOrderDao, order_dao: OrderDao):
        self.logger = logger
        self.state_machine: Dict = state_machine
        self.exchanges_by_id: Dict[int, ExchangeServiceAbc] = exchanges_by_id
        self.order_dao = order_dao
        self.open_order_dao = open_order_dao

    def state(self, f):
        def wrapper():
            self.logger.debug('start state {0}'.format(f.__name__))
            f()
            self.logger.debug('end state {0}'.format(f.__name__))
            return wrapper

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

    # @state
    # def archive_trade(s):
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
    state = staticmethod(state)
