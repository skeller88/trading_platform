"""
Test exchange live functionality.

Exchanges won't allow for multiple accounts per exchange. So, the same exchange has to be used for trading
and testing. This creates some trickiness, for example, when asserting the number of open orders is as expected,
the number of open orders could vary depending on which production orders were placed.
"""
from nose.tools import eq_
from trading_platform.exchanges.data.financial_data import FinancialData

from trading_platform.exchanges.data.pair import Pair

from trading_platform.exchanges.data.enums.order_status import OrderStatus

from trading_platform.exchanges.data.utils import check_required_fields

from trading_platform.exchanges.data.order import Order

from trading_platform.exchanges.live.binance_live_service import BinanceLiveService
from trading_platform.exchanges.test.live.test_live_exchange_service import TestLiveExchangeService


class TestBinanceLiveService(TestLiveExchangeService):
    __test__ = True

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.live_service_class = BinanceLiveService
        cls.xrp_tag_len = 9
        cls.sleep_sec_consistency = 10

        cls.exchange_order_id_for_filled_order = '51786981'
        cls.pair_for_filled_order = Pair(base='BTC', quote='XRP')

        cls.exchange_order_id_for_cancelled_order = '427755'
        cls.pair_for_cancelled_order = Pair(base='BTC', quote='ZEN')

        cls.fields_to_ignore = [
            'exchange_order_id',
            'order_status',
            'app_create_timestamp',
            'exchange_timestamp',
        ]
        cls.fields_to_ignore.extend(Order.financial_data_fields)

    def test_fetch_cancelled_order(self):
        """
        Fetch an order that's been filled. Responses should be as expected.

        Returns:

        """
        order: Order = self.service.fetch_order(exchange_order_id=self.exchange_order_id_for_cancelled_order,
                                                pair=self.pair_for_cancelled_order, params=None)
        check_required_fields(order)
        eq_(order.exchange_id, self.live_service_class.exchange_id)
        assert (order.exchange_order_id is not None)
        eq_(order.order_status, OrderStatus.cancelled)

    def test_fetch_filled_order(self):
        """
        Fetch an order that's been filled. Responses should be as expected.

        Returns:

        """
        order: Order = self.service.fetch_order(exchange_order_id=self.exchange_order_id_for_filled_order,
                                                pair=self.pair_for_filled_order, params=None)
        check_required_fields(order)
        eq_(order.exchange_id, self.live_service_class.exchange_id)
        assert (order.exchange_order_id is not None)
        eq_(order.order_status, OrderStatus.filled)

    def test_buy_order_crud(self):
        self.validate_buy_order_crud(self.fields_to_ignore, decimal_comparison_precision=FinancialData.two_places)

    def test_sell_order_crud(self):
        self.validate_sell_order_crud(self.fields_to_ignore, decimal_comparison_precision=FinancialData.two_places)
