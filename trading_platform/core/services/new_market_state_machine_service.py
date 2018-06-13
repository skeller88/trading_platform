from abc import ABC
from typing import Dict, Set, List, Callable

from trading_platform.exchanges.data.enums import exchange_ids

from trading_platform.core.services.strategy_state_machine_service_abc import StrategyStateMachineServiceAbc, state
from trading_platform.exchanges.data.enums.order_side import OrderSide
from trading_platform.exchanges.data.financial_data import FinancialData
from trading_platform.exchanges.data.order import Order
from trading_platform.exchanges.data.pair import Pair
from trading_platform.exchanges.data.ticker import Ticker
from trading_platform.exchanges.exchange_service_abc import ExchangeServiceAbc
from trading_platform.storage.daos.open_order_dao import OpenOrderDao
from trading_platform.storage.daos.order_dao import OrderDao


class NewMarketStateMachineService(StrategyStateMachineServiceAbc):
    def __init__(self, logger, exchanges_by_id: Dict[int, ExchangeServiceAbc],
                 open_order_dao: OpenOrderDao, order_dao: OrderDao, sell_price: FinancialData, sell_price_adjuster: Callable):
        state: Dict = {
            'current_state': 'initialize',
            'state_id': None,
            'initialize': {
                'completed': False,
                'success': self.buy
            },
            'buy': {
                'completed': False,
                'success': self.verify_buy,
            },
            'verify_buy': {
                'completed': False,
                'success': self.watch_order
            },
            'watch': {
                'completed': False,
                'success': self.adjust_sell_price
            },
            'adjust_sell_price': {
                'completed': False,
                'success': self.watch_order
            },
            'verify_sell': {
                'completed': False,
                'success': self.finish
            }
        }
        super().__init__(state=state, logger=logger, exchanges_by_id=exchanges_by_id,
                         open_order_dao=open_order_dao, order_dao=order_dao)
        self.sell_price: FinancialData = sell_price
        self.sell_price_adjuster: Callable = sell_price_adjuster
        self.bittrex = exchanges_by_id.get(exchange_ids.bittrex)
        self.buy_order: Order = None
        self.pair: Pair = None

    @state
    def buy(self, buy_order: Order):
        orders_placed: List[Order] = self.place_orders(Set(buy_order), None)
        self.next_state()
        self.buy_order = orders_placed[0]
        self.pair = Pair(base=self.buy_order.base, quote=self.buy_order.quote)

    @state
    def verify_buy(self):
        for attempt in range(3):
            try:
                open_orders: Dict[str, Order] = self.bittrex.fetch_open_orders(self.pair.name_for_exchange_clients)
                if open_orders.get(self.buy_order.order_index):
                    self.next_state()
            except Exception:
                self.next_state(self.buy_completion_failed)


    @state
    def buy_completion_failed(self):
        pass


    @state
    def watch_order(self):
        while True:
            # TODO - ugly to have 2 function calls. Fix.
            self.bittrex.fetch_latest_tickers()
            tickers: Dict[str, Ticker] = self.bittrex.get_tickers()
            ticker: Ticker = tickers.get(self.pair.name)

            sell_price_adjuster: FinancialData = self.sell_price_adjuster(ticker)
            if sell_price_adjuster:
                self.next_state(self.adjust_sell_price, sell_price_adjuster)


    @state
    def adjust_sell_price(self, sell_price_adjuster):
        # TODO - cancel previous sell order, if any

        quote_balance: FinancialData = self.bittrex.fetch_balances().get(self.pair.quote)

        sell_order = Order(**{
            'exchange_id': self.bittrex.exchange_id,

            'amount': quote_balance,
            'price': sell_price_adjuster,

            'base': self.pair.base,
            'quote': self.pair.quote,
            'order_side': OrderSide.sell
        })
        orders_placed: List[Order] = self.place_orders(Set(sell_order), None)
        self.next_state()
        self.sell_order = orders_placed[0]

    @state
    def verify_sell(self):
        for attempt in range(3):
            try:
                open_orders: Dict[str, Order] = self.bittrex.fetch_open_orders(self.pair.name_for_exchange_clients)
                if open_orders.get(self.sell_order.order_index):
                    self.next_state()
            except Exception:
                self.next_state(self.sell_completion_failed)


    @state
    def sell_completion_failed(self):
        pass

    @state
    def finish(self):
        pass
