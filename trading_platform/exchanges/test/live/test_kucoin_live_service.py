from trading_platform.exchanges.test.live.test_live_exchange_service import TestLiveExchangeService

from trading_platform.exchanges.live.kucoin_live_service import KucoinLiveService


class TestKucoinLiveService(TestLiveExchangeService):
    __test__ = True
    live_service_class = KucoinLiveService