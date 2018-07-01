from trading_platform.exchanges.live.kucoin_live_service import KucoinLiveService
from trading_platform.exchanges.test.live.test_live_exchange_service import TestLiveExchangeService


class TestKucoinLiveService(TestLiveExchangeService):
    __test__ = True

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.live_service_class = KucoinLiveService
        cls.sleep_sec_consistency = 6

        cls.fields_to_ignore = [
            'exchange_order_id',
            'order_status',
            'app_create_timestamp',
            'exchange_timestamp'
        ]

    def test_buy_order_crud(self):
        self.validate_buy_order_crud(self.fields_to_ignore, None)

    def test_sell_order_crud(self):
        self.validate_sell_order_crud(self.fields_to_ignore, None)
