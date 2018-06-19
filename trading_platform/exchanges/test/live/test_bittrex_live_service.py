"""
Test exchange live functionality.

Exchanges won't allow for multiple accounts per exchange. So, the same exchange has to be used for trading
and testing. This creates some trickiness, for example, when asserting the number of open orders is as expected,
the number of open orders could vary depending on which production orders were placed.
"""
from time import sleep
from typing import Dict, Callable

from nose.tools import eq_, assert_almost_equal, assert_true, nottest, assert_greater

from trading_platform.core.test.util_methods import eq_ignore_certain_fields
from trading_platform.exchanges.data.enums import exchange_ids
from trading_platform.exchanges.data.enums.order_side import OrderSide
from trading_platform.exchanges.data.enums.order_status import OrderStatus
from trading_platform.exchanges.data.enums.order_type import OrderType
from trading_platform.exchanges.data.financial_data import zero, FinancialData, one
from trading_platform.exchanges.data.order import Order
from trading_platform.exchanges.data.pair import Pair
from trading_platform.exchanges.data.utils import check_required_fields
from trading_platform.exchanges.live.bittrex_live_service import BittrexLiveService
from trading_platform.exchanges.test.live.test_live_exchange_service import TestLiveExchangeService


class TestBittrexLiveService(TestLiveExchangeService):
    __test__ = True
    live_service_class = BittrexLiveService
    xrp_tag_len = 10
    exchange_order_id_for_filled_order = '54ee8a42-0354-423e-9d23-8226c4a8e9c7'
    exchange_order_id_for_cancelled_order = '309ab197-83e9-49e0-90ac-7c9942ec010b'

    def test_fetch_cancelled_order(self):
        """
        Fetch an order that's been filled. Responses should be as expected.

        Returns:

        """
        order: Order = self.service.fetch_order(exchange_order_id=self.exchange_order_id_for_cancelled_order)
        check_required_fields(order)
        eq_(order.exchange_id, self.live_service_class.exchange_id)
        assert (order.exchange_order_id is not None)
        eq_(order.order_status, OrderStatus.cancelled)

    def test_fetch_filled_order(self):
        """
        Fetch an order that's been filled. Responses should be as expected.

        Returns:

        """
        order: Order = self.service.fetch_order(exchange_order_id=self.exchange_order_id_for_filled_order)
        check_required_fields(order)
        eq_(order.exchange_id, self.live_service_class.exchange_id)
        assert (order.exchange_order_id is not None)
        eq_(order.order_status, OrderStatus.filled)

    def test_buy_order_crud(self):
        """
        Should be able to place orders, fetch open orders, and cancel orders.

        Assumes that the exchange has BTC and USDT balances, each balance > $30 which is the trading minimum.

        There's no way to run this test with test orders, so create sell orders with very high prices and buy
        orders with very low prices.

        Returns:

        """
        self.service.fetch_latest_tickers()
        balances = self.service.fetch_balances()
        quote_ticker = self.service.get_ticker(self.pair.name)
        quote_buy_price = quote_ticker.bid * (one - FinancialData(.2))

        base_order_kwargs: Dict = {
            'base': self.pair.base,
            'quote': self.pair.quote,

            'exchange_id': self.service.exchange_id,
            'order_status': OrderStatus.pending,
            'order_type': OrderType.limit
        }
        fields_to_ignore = [
            'exchange_order_id',
            'order_status',
            'app_create_timestamp',
            'exchange_timestamp'
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
            # compare buy_order with open_buy_order
            eq_ignore_certain_fields(buy_order, open_buy_order, fields_to_ignore=fields_to_ignore)

            # numerical data
            assert_almost_equal(buy_order.amount, buy_amount, places=FinancialData.six_places)
            assert_almost_equal(buy_order.price, quote_buy_price, places=FinancialData.six_places)
            assert_almost_equal(buy_order.remaining, buy_order.amount, places=FinancialData.six_places)

            # metadata
            eq_(buy_order.order_side, OrderSide.buy)

            # same fields for pending buy and sell orders
            check_required_fields(buy_order)

            assert (buy_order.exchange_order_id is None)
            eq_(buy_order.order_status, OrderStatus.pending)

            # same fields for opened buy and sell orders
            eq_(buy_order.exchange_id, self.service.exchange_id)
            eq_(buy_order.order_type, OrderType.limit)
            eq_(buy_order.base, self.pair.base)
            eq_(buy_order.quote, self.pair.quote)

            # order_status and exchange_order_id should be different
            assert (buy_order.exchange_order_id is not None)
            eq_(buy_order.order_status, OrderStatus.open)

            assert_almost_equal(buy_order.filled, zero, places=FinancialData.six_places)

            sleep(self.sleep_sec_consistency)

            open_orders: Dict[str, Order] = self.service.fetch_open_orders(
                Pair(base=self.pair.base, quote=self.pair.quote))
            assert_true(len(open_orders) >= 2)

            open_buy_order = self.service.get_order(buy_order.order_id)
            check_required_fields(open_buy_order)
            eq_ignore_certain_fields(open_buy_order, buy_order, fields_to_ignore=fields_to_ignore)

            cancelled_buy_order = self.service.cancel_order(order=open_buy_order.exchange_order_id)
            eq_(cancelled_buy_order.order_id, open_buy_order.order_id)
            eq_(cancelled_buy_order.order_status, OrderStatus.cancelled)

            sleep(self.sleep_sec_consistency)

            open_orders: Dict[str, Order] = self.service.fetch_open_orders(
                Pair(base=self.pair.base, quote=self.pair.quote))
            eq_(len(open_orders), 0)

            open_buy_order = self.service.get_order(buy_order.order_id)
            assert (open_buy_order is None)
        # clean up any placed orders even if there's an exception.
        finally:
            try:
                self.service.cancel_order(order=buy_order.exchange_order_id)
            # will throw an exception if order was already cancelled
            except Exception:
                pass

    def test_sell_order_crud(self):
        """
         Should be able to place orders, fetch open orders, and cancel orders.

         Assumes that the exchange has BTC and USDT balances, each balance > $30 which is the trading minimum.

         There's no way to run this test with test orders, so create sell orders with very high prices and buy
         orders with very low prices.

         Returns:

         """
        self.service.fetch_latest_tickers()
        balances = self.service.fetch_balances()
        quote_ticker = self.service.get_ticker(self.pair.name)
        quote_sell_price = quote_ticker.ask * (one + FinancialData(.2))

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
        self.test_order_crud(sell_order_kwargs)

    @nottest
    def test_order_crud(self, order_kwargs):
        """
          Should be able to place orders, fetch open orders, and cancel orders.

          Assumes that the exchange has BTC and USDT balances, each balance > $30 which is the trading minimum.

          There's no way to run this test with test orders, so create sell orders with very high prices and buy
          orders with very low prices.

          Returns:

          """
        self.service.fetch_latest_tickers()

        base_order_kwargs: Dict = {
            'base': self.pair.base,
            'quote': self.pair.quote,

            'exchange_id': self.service.exchange_id,
            'order_status': OrderStatus.pending,
            'order_type': OrderType.limit
        }

        fields_to_ignore = [
            'exchange_order_id',
            'order_status',
            'app_create_timestamp'
        ]

        base_order_kwargs.update(order_kwargs)
        order: Order = Order(**base_order_kwargs)
        exchange_method: Callable = self.service.create_limit_buy_order if order.order_side == OrderSide.buy else self.service.create_limit_sell_order
        open_order = exchange_method(order=order)

        # compare order with open_order
        eq_ignore_certain_fields(order, open_order, fields_to_ignore=fields_to_ignore)

        # same fields for pending buy and sell orders
        check_required_fields(order)

        # same fields for opened buy and sell orders
        eq_(order.exchange_id, self.service.exchange_id)
        eq_(order.order_type, OrderType.limit)
        eq_(order.base, self.pair.base)
        eq_(order.quote, self.pair.quote)

        # The following fields are different between an open order and a pending order:
        # 'exchange_order_id',
        assert (order.exchange_order_id is None)
        assert (open_order.exchange_order_id is not None)

        # 'order_status',
        eq_(order.order_status, OrderStatus.pending)
        eq_(open_order.order_status, OrderStatus.open)

        # 'app_create_timestamp',
        assert_greater(open_order.app_create_timestamp, order.app_create_timestamp)

        sleep(self.sleep_sec_consistency)

        open_orders: Dict[str, Order] = self.service.fetch_open_orders(
            Pair(base=self.pair.base, quote=self.pair.quote))
        assert_true(len(open_orders) == 1)

        open_order = self.service.get_order(order.order_id)
        check_required_fields(open_order)

        # This sucks, but the exchange data returned by the create_limit call is different from the
        # exchange data returned by the fetch_open_orders call.
        fields_to_ignore.append('exchange_timestamp')
        eq_ignore_certain_fields(open_order, order, fields_to_ignore=fields_to_ignore)
        assert(open_order.exchange_timestamp is not None)

        cancelled_buy_order = self.service.cancel_order(order=open_order)
        eq_(cancelled_buy_order.order_id, open_order.order_id)
        eq_(cancelled_buy_order.order_status, OrderStatus.cancelled)

        sleep(self.sleep_sec_consistency)

        open_orders: Dict[str, Order] = self.service.fetch_open_orders(
            Pair(base=self.pair.base, quote=self.pair.quote))
        eq_(len(open_orders), 0)

        open_order = self.service.get_order(order.order_id)
        assert (open_order is None)