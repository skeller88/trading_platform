import unittest

from trading_platform.data_engineering.ticker_fetcher import lambda_handler


class TickerFetcherTest(unittest.TestCase):
    def test_main(self):
        """
        Should fetch tickers from all exchanges and save them to a csv file.
        TODO - AWS can't serialize the response from this function, so right now the function returns None.
        should return a list of fetched Ticker instances.
        Returns:

        """
        expected_tickers = lambda_handler.main(None, None)
        # ticker = expected_tickers[0]
        # check_required_fields(ticker)

        # About 730 tickers were being returned for all exchanges as of 4/4/2018.
        # assert_greater(len(expected_tickers), 700)

        # tickers for all exchanges should be saved
        # unique_exchange_ids = set(map(lambda x: x.exchange_id, expected_tickers))
        # map(lambda id: assert_true(id in unique_exchange_ids), exchange_ids.all_ids)
