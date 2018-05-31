"""
Test exchange live functionality.

Exchanges won't allow for multiple accounts per exchange. So, the same exchange has to be used for trading
and testing. This creates some trickiness, for example, when asserting the number of open orders is as expected,
the number of open orders could vary depending on which production orders were placed.
"""
from time import sleep

from nose.tools import eq_, assert_almost_equal, assert_true

from trading_platform.exchanges.data.enums import exchange_ids
from trading_platform.exchanges.data.enums.order_side import OrderSide
from trading_platform.exchanges.data.enums.order_status import OrderStatus
from trading_platform.exchanges.data.enums.order_type import OrderType
from trading_platform.exchanges.data.financial_data import zero, FinancialData, one
from trading_platform.exchanges.data.utils import check_required_fields
from trading_platform.exchanges.live.binance_live_service import BinanceLiveService
from trading_platform.core.test import data
from trading_platform.core.test.services.exchange.live.test_live_exchange_service import TestLiveExchangeService
from trading_platform.core.test.util_methods import eq_ignore_certain_fields


class TestBinanceLiveService(TestLiveExchangeService):
    __test__ = True
    live_service_class = BinanceLiveService
    xrp_tag_len = 9

    def test_order_crud(self):
        """
        Should be able to place orders, fetch open orders, and cancel orders.

        Assumes that the exchange has ETH and USDT balances, each balance > $30 which is the trading minimum.

        There's no way to run this test with test orders, so create sell orders with very high prices and buy
        orders with very low prices.

        Returns:

        """
        self.service.fetch_latest_tickers()
        quote_ticker = self.service.get_ticker(self.pair.name)
        quote_sell_price = quote_ticker.ask * (one + FinancialData(.2))
        quote_buy_price = quote_ticker.bid * (one - FinancialData(.2))

        # Only Bittrex has a ETH balance, so no sell order is placed.
        # TODO - place sell order
        buy_amount = data.minimum_usdt_balance / quote_buy_price
        buy_order = self.service.create_limit_buy_order(pair=self.pair, price=quote_buy_price, amount=buy_amount)

        try:
            # unlike in the case of bittrex, the binance response populates these values. The response
            # precision is to the 2nd decimal place.
            precision = FinancialData.five_places if self.live_service_class.exchange_id == exchange_ids.bittrex else 2

            # Buy order should have expected fields
            check_required_fields(buy_order)
            # exchange-related data
            eq_(buy_order.exchange_id, self.service.exchange_id)

            # numerical data
            assert_almost_equal(buy_order.amount, buy_amount, places=precision)
            assert_almost_equal(buy_order.filled, zero, places=precision)
            assert_almost_equal(buy_order.price, quote_buy_price, places=precision)
            assert_almost_equal(buy_order.remaining, buy_order.amount, places=precision)

            # metadata
            eq_(buy_order.order_type, OrderType.limit)
            eq_(buy_order.order_status, OrderStatus.open)
            eq_(buy_order.order_side, OrderSide.buy)
            eq_(buy_order.base, self.pair.base)
            eq_(buy_order.quote, self.pair.quote)

            sleep(self.sleep_sec_consistency)

            # Unlike Binance, Bittrex create limit order responses don't have the following fields
            numerical_fields = ['amount', 'filled', 'price', 'remaining']
            fields_to_ignore = ['processing_time',
                                'event_time'] + numerical_fields if self.live_service_class.exchange_id == exchange_ids.bittrex else [
                'processing_time']

            open_orders = self.fetch_open_orders_for_order_instances(self.service, [buy_order])
            assert_true(len(open_orders) >= 1)

            open_buy_order = self.service.get_open_order(buy_order.order_index)
            check_required_fields(open_buy_order)
            eq_ignore_certain_fields(open_buy_order, buy_order, fields_to_ignore=fields_to_ignore)

            cancelled_buy_order = self.service.cancel_order(pair=self.pair, order_id=buy_order.order_id)
            eq_(cancelled_buy_order.order_index, buy_order.order_index)
            eq_(cancelled_buy_order.order_status, OrderStatus.cancelled)

            sleep(self.sleep_sec_consistency)

            open_orders = self.fetch_open_orders_for_order_instances(self.service, [buy_order])
            eq_(len(open_orders), 0)

            open_buy_order = self.service.get_open_order(buy_order.order_index)
            assert (open_buy_order is None)
        # clean up any placed orders even if there's an exception.
        finally:
            try:
                self.service.cancel_order(pair=self.pair, order_id=buy_order.order_id)
            # will throw an exception if order was already cancelled
            except Exception:
                pass
