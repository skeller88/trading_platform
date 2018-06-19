"""
Test exchange live functionality.

Exchanges won't allow for multiple accounts per exchange. So, the same exchange has to be used for trading
and testing. This creates some trickiness, for example, when asserting the number of open orders is as expected,
the number of open orders could vary depending on which production orders were placed.
"""
from time import sleep
from typing import Dict

from nose.tools import eq_, assert_almost_equal, assert_true

from trading_platform.core.test.util_methods import eq_ignore_certain_fields
from trading_platform.exchanges.data.enums import exchange_ids
from trading_platform.exchanges.data.enums.order_side import OrderSide
from trading_platform.exchanges.data.enums.order_status import OrderStatus
from trading_platform.exchanges.data.enums.order_type import OrderType
from trading_platform.exchanges.data.financial_data import zero, FinancialData, one
from trading_platform.exchanges.data.order import Order
from trading_platform.exchanges.data.utils import check_required_fields
from trading_platform.exchanges.live.bittrex_live_service import BittrexLiveService
from trading_platform.exchanges.test.live.test_live_exchange_service import TestLiveExchangeService


class TestBittrexLiveService(TestLiveExchangeService):
    __test__ = True
    live_service_class = BittrexLiveService
    xrp_tag_len = 10

    def test_fetch_filled_order(self):
        """
        Fetch an order that's been filled. Responses should be as expected.

        Returns:

        """
        exchange_order_id: str = '54ee8a42-0354-423e-9d23-8226c4a8e9c7'
        order: Order = self.service.fetch_order(exchange_order_id=exchange_order_id)
        check_required_fields(order)
        eq_(order.exchange_id, self.live_service_class.exchange_id)
        eq_()

    def test_order_crud(self):
        """
        Should be able to place orders, fetch open orders, and cancel orders.

        Assumes that the exchange has ETH and USDT balances, each balance > $30 which is the trading minimum.

        There's no way to run this test with test orders, so create sell orders with very high prices and buy
        orders with very low prices.

        Returns:

        """
        self.service.fetch_latest_tickers()
        balances = self.service.fetch_balances()
        quote_ticker = self.service.get_ticker(self.pair.name)
        quote_sell_price = quote_ticker.ask * (one + FinancialData(.2))
        quote_buy_price = quote_ticker.bid * (one - FinancialData(.2))

        base_order_kwargs: Dict = {
            'base': self.pair.base,
            'quote': self.pair.quote,

            'exchange_id': self.service.exchange_id,
            'order_status': OrderStatus.pending,
            'order_type': OrderType.limit
        }
        # Only Bittrex has a BTC balance
        sell_amount = self.service.get_balance(self.pair.quote).free
        sell_order_kwargs: Dict = {
            'amount': sell_amount,
            'price': quote_sell_price,

            'order_side': OrderSide.sell,
            # The following Order.financial_data_fields are not populated by the exchange response
            'remaining': sell_amount,
            'filled': zero,
        }
        sell_order_kwargs.update(base_order_kwargs)
        sell_order: Order = Order(**sell_order_kwargs)
        open_sell_order: Order = self.service.create_limit_sell_order(order=sell_order)
        fields_to_ignore = [
            'exchange_order_id',
            'order_status',
            'app_create_timestamp'
        ]

        buy_amount = self.service.get_balance(self.pair.base).free / quote_buy_price * FinancialData(.9)
        buy_order_kwargs: Dict = {
            'amount': buy_amount,
            'price': quote_buy_price,

            'order_side': OrderSide.buy,
            # The following Order.financial_data_fields are not populated by the exchange response
            'remaining': buy_amount,
            'filled': zero,
        }
        buy_order_kwargs.update(base_order_kwargs)
        buy_order: Order = Order(**buy_order_kwargs)
        open_buy_order = self.service.create_limit_buy_order(order=buy_order)

        try:
            # compare with order returned from exchange
            eq_ignore_certain_fields(sell_order, open_sell_order, fields_to_ignore=fields_to_ignore)

            # numerical data
            # unlike in the case of bittrex, the binance response populates these values. The response
            # precision is to the 2nd decimal place.
            precision = FinancialData.five_places if self.live_service_class.exchange_id == exchange_ids.bittrex else 2

            assert_almost_equal(sell_order.amount, sell_amount, places=precision)
            assert_almost_equal(sell_order.price, quote_sell_price, places=precision)
            assert_almost_equal(sell_order.remaining, sell_order.amount, places=precision)

            # metadata
            eq_(sell_order.order_side, OrderSide.sell)

            # compare buy_order with open_buy_order
            eq_ignore_certain_fields(buy_order, open_buy_order, fields_to_ignore=fields_to_ignore)

            # numerical data
            assert_almost_equal(buy_order.amount, buy_amount, places=precision)
            assert_almost_equal(buy_order.price, quote_buy_price, places=precision)
            assert_almost_equal(buy_order.remaining, buy_order.amount, places=precision)

            # metadata
            eq_(buy_order.order_side, OrderSide.buy)

            # same fields for pending buy and sell orders
            for order in [buy_order, sell_order]:
                check_required_fields(order)

                assert (order.exchange_order_id is None)
                eq_(order.order_status, OrderStatus.pending)

            # same fields for opened buy and sell orders
            for order in [open_buy_order, open_sell_order]:
                eq_(order.exchange_id, self.service.exchange_id)
                eq_(order.order_type, OrderType.limit)
                eq_(order.base, self.pair.base)
                eq_(order.quote, self.pair.quote)

                # order_status and exchange_order_id should be different
                assert (order.exchange_order_id is not None)
                eq_(order.order_status, OrderStatus.open)

                assert_almost_equal(order.filled, zero, places=precision)

            sleep(self.sleep_sec_consistency)

            # Unlike Binance, Bittrex create limit order responses don't have the following fields
            fields_to_ignore = ['app_create_timestamp',
                                'exchange_timestamp'] + Order.financial_data_fields if self.live_service_class.exchange_id == exchange_ids.bittrex else [
                'app_create_timestamp']

            open_orders = self.fetch_open_orders_for_order_instances(self.service, [buy_order, sell_order])
            assert_true(len(open_orders) >= 2)

            open_sell_order = self.service.get_order(sell_order.order_id)
            check_required_fields(open_sell_order)

            eq_ignore_certain_fields(open_sell_order, sell_order, fields_to_ignore=fields_to_ignore)

            open_buy_order = self.service.get_order(buy_order.order_id)
            check_required_fields(open_buy_order)
            eq_ignore_certain_fields(open_buy_order, buy_order, fields_to_ignore=fields_to_ignore)

            cancelled_sell_order = self.service.cancel_order(pair=self.pair, exchange_order_id=sell_order.exchange_order_id)
            eq_(cancelled_sell_order.order_id, sell_order.order_id)
            eq_(cancelled_sell_order.order_status, OrderStatus.cancelled)

            cancelled_buy_order = self.service.cancel_order(pair=self.pair, exchange_order_id=buy_order.exchange_order_id)
            eq_(cancelled_buy_order.order_id, buy_order.order_id)
            eq_(cancelled_buy_order.order_status, OrderStatus.cancelled)

            sleep(self.sleep_sec_consistency)

            open_orders = self.fetch_open_orders_for_order_instances(self.service, [buy_order, sell_order])
            eq_(len(open_orders), 0)
            open_sell_order = self.service.get_order(sell_order.order_id)
            assert (open_sell_order is None)

            open_buy_order = self.service.get_order(buy_order.order_id)
            assert (open_buy_order is None)
        # clean up any placed orders even if there's an exception.
        finally:
            try:
                for order in [open_buy_order, open_sell_order]:
                    self.service.cancel_order(pair=self.pair, exchange_order_id=order.exchange_order_id)
            # will throw an exception if order was already cancelled
            except Exception:
                pass
