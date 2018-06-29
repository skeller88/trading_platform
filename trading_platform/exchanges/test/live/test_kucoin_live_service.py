from typing import Dict

from trading_platform.exchanges.data.enums.order_side import OrderSide
from trading_platform.exchanges.data.financial_data import one, FinancialData, zero
from trading_platform.exchanges.data.order import Order
from trading_platform.exchanges.test.live.test_live_exchange_service import TestLiveExchangeService

from trading_platform.exchanges.live.kucoin_live_service import KucoinLiveService


class TestKucoinLiveService(TestLiveExchangeService):
    __test__ = True
    live_service_class = KucoinLiveService
    sleep_sec_consistency = 6

    def test_buy_order_crud(self):
        fields_to_ignore = [
            'exchange_order_id',
            'order_status',
            'app_create_timestamp',
            'exchange_timestamp'
        ]
        self.validate_buy_order_crud(fields_to_ignore)

    def test_sell_order_crud(self):
        fields_to_ignore = [
            'exchange_order_id',
            'order_status',
            'app_create_timestamp',
            'exchange_timestamp'
        ]
        self.validate_sell_order_crud(fields_to_ignore)