from typing import Set, List

from trading_platform.exchanges.data.order import Order


class TradeSaga:
    def __init__(self, orders: Set[Order]):
        self.orders = orders