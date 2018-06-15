import unittest

from nose.tools import eq_, assert_greater

from trading_platform.exchanges.data.enums import exchange_ids
from trading_platform.exchanges.data.pair import Pair
from trading_platform.exchanges.data.utils import check_required_fields
from trading_platform.exchanges.live.live_subclasses import exchange_service_credentials_for_exchange


class TestLiveExchangeServiceLimited(unittest.TestCase):
    """
    Tests a live exchange service, but with more limited functionality than would be tested by
    TestLiveExchangeService. No orders are placed, so this test class can be run against exchange accounts that
    are live trading.
    """
    __test__ = False  # important, makes sure tests are not run on base class
    # Each inheritor of this class will set these values
    live_service_class = None

    @classmethod
    def setUpClass(cls):

        if cls.live_service_class.exchange_id == exchange_ids.gdax:
            cls.service = cls.live_service_class(None, None, withdrawal_fees=None)
        else:
            credentials = exchange_service_credentials_for_exchange(cls.live_service_class)
            cls.service = cls.live_service_class(credentials.get('key'), credentials.get('secret'),
                                             withdrawal_fees=None)
        cls.pair = Pair(base='BTC', quote='ETH')

    ###########################################
    # Market state
    ###########################################
    def test_fetch_latest_tickers(self):
        eq_(len(self.service.get_tickers()), 0)
        self.service.fetch_latest_tickers()
        # Gdax has the fewest amount of tickers at 6
        assert len(self.service.get_tickers()) >= 6

        ticker = self.service.get_ticker(self.pair.name)
        check_required_fields(ticker)
        eq_(ticker.base, self.pair.base)
        eq_(ticker.quote, self.pair.quote)

    def test_load_markets(self):
        if self.service.exchange_id == exchange_ids.gdax:
            assert_greater(len(self.service.load_markets()), 10)
        else:
            assert_greater(len(self.service.load_markets()), 50)