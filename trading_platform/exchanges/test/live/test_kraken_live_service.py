from trading_platform.exchanges.live.kraken_live_service import KrakenLiveService
from trading_platform.exchanges.test.live.test_live_exchange_service_limited import TestLiveExchangeServiceLimited


class TestKrakenLiveService(TestLiveExchangeServiceLimited):
    __test__ = True
    live_service_class = KrakenLiveService