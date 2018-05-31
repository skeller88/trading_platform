from trading_platform.exchanges.live.poloniex_live_service import PoloniexLiveService
from trading_platform.core.test.services.exchange.live.test_live_exchange_service_limited import TestLiveExchangeServiceLimited


class TestPoloniexLiveService(TestLiveExchangeServiceLimited):
    __test__ = True
    live_service_class = PoloniexLiveService