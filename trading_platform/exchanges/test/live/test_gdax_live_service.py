from trading_platform.exchanges.live.gdax_live_service import GdaxLiveService
from trading_platform.exchanges.test.live.test_live_exchange_service_limited import TestLiveExchangeServiceLimited


class TestGdaxLiveService(TestLiveExchangeServiceLimited):
    __test__ = True
    live_service_class = GdaxLiveService