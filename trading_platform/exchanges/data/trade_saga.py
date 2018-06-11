from typing import Set, List

from trading_platform.exchanges.data.order import Order


class TradeSaga:
    def __init__(self, strategy_execution_id: str, trade_saga_id: str, orders: Set[Order]):
        self.strategy_execution_id: str = strategy_execution_id
        self.trade_saga_id: str = trade_saga_id
        self.orders: Set[Order] = orders