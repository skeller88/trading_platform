from typing import Callable, Optional

from trading_platform.exchanges.data.order import Order


class TrailingStopExecuter:
    def __init__(self, initial_order: Order, stop_adjuster: Callable):
        self.initial_order = initial_order
        self.current_order: Optional[Order] = None
        self.stop_adjuster = stop_adjuster

    def run(self):
        next_stop_price = self.stop_adjuster
        if self.current_order is None:

