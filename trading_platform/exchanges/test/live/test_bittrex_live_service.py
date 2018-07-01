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

    @classmethod
    def setUpClass(cls):
        cls.live_service_class = BittrexLiveService
        cls.xrp_tag_len = 10
        cls.exchange_order_id_for_filled_order = '54ee8a42-0354-423e-9d23-8226c4a8e9c7'
        cls.exchange_order_id_for_cancelled_order = '309ab197-83e9-49e0-90ac-7c9942ec010b'

        cls.fields_to_ignore = [
            'exchange_order_id',
            'order_status',
            'app_create_timestamp',
        ]

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

    # def test_cancel_filled_order(self):
    #     order_to_cancel: Order = Order(**{
    #         'base': self.pair.base,
    #         'quote': self.pair.quote,
    #
    #         'exchange_id': self.service.exchange_id,
    #         'exchange_order_id': self.exchange_order_id_for_filled_order,
    #     })
    #
    #     order_cancelled: Order = self.service.cancel_order(order=order_to_cancel)

    def test_buy_order_crud(self):
        self.validate_buy_order_crud(self.fields_to_ignore, None)

    def test_sell_order_crud(self):
        self.validate_sell_order_crud(self.fields_to_ignore, None)
