import csv
import unittest
from collections import defaultdict

from nose.tools import assert_greater, eq_

from trading_platform.exchanges.data.enums import exchange_ids
from trading_platform.exchanges.data.ticker import Ticker
from trading_platform.exchanges.data.utils import check_required_fields
from trading_platform.exchanges.live import live_subclasses
from trading_platform.exchanges.ticker_service import TickerService


class TestTickerService(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Only Binance and Bittrex have test accounts right now.
        # TODO - add test account for every exchange.
        cls.exchange_services = live_subclasses.instantiate(live_subclasses.all_live(),
                                                            withdrawal_fees_by_exchange=defaultdict(None))
        cls.ticker_service_class = TickerService

    def test_fetch_latest_tickers(self):
        """
        Tickers should be returned for every exchange, and the approximate number of tickers across all exchanges
        should be returned.
        Returns:

        """
        tickers = self.ticker_service_class.fetch_latest_tickers(self.exchange_services)

        ticker: Ticker = tickers[0]
        TestTickerService.validate_ticker(ticker)
        # As of 4/26/2018, there were 738 tickers across all 5 exchanges.
        assert_greater(len(tickers), 730)
        exchange_ids_set = set()
        list(map(lambda ticker: exchange_ids_set.add(ticker.exchange_id), tickers))
        eq_(len(exchange_ids_set), len(self.exchange_services))

    def test_fetch_latest_tickers_and_save(self):
        filepath, tickers = self.ticker_service_class.fetch_latest_tickers_and_save(self.exchange_services)
        # As of 4/26/2018, there were 738 tickers across all 5 exchanges.
        assert_greater(len(tickers), 730)
        exchange_ids_set = set()
        list(map(lambda ticker: exchange_ids_set.add(ticker.exchange_id), tickers))
        eq_(len(exchange_ids_set), len(self.exchange_services))

        with open(filepath, 'r') as fileobj:
            reader = csv.DictReader(fileobj)
            num_rows = 0
            for row in reader:
                num_rows += 1
                ticker = Ticker.from_csv_data(row, Ticker.current_version)
                TestTickerService.validate_ticker(ticker)

            eq_(num_rows, len(tickers))

    @staticmethod
    def validate_ticker(ticker):
        check_required_fields(ticker)

        volume_fields_to_check = ['base_volume'] if ticker.exchange_id == exchange_ids.gdax else [
            'base_volume', 'quote_volume']

        if int(ticker.version) >= ticker.first_version_with_volume_fields:
            for field in volume_fields_to_check:
                assert (getattr(ticker, field) is not None)
