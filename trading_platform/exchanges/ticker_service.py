import itertools
import time
from typing import List, Dict

import pandas

from trading_platform.aws_utils.s3_operations import write_tickers
from trading_platform.exchanges.data.enums import exchange_ids
from trading_platform.exchanges.data.pair import Pair
from trading_platform.exchanges.data.ticker import Ticker
from trading_platform.exchanges.exchange_service_abc import ExchangeServiceAbc
from trading_platform.properties import env_properties
from trading_platform.utils.logging import print_if_debug_enabled


class TickerService:
    """
    Fetch and save tickers for all exchanges
    """

    def run_ticker_service(self, debug, exchange_services):
        print_if_debug_enabled(debug, 'start fetch_latest_tickers')
        start_fetch_ticker = time.time()
        tickers_list = TickerService.fetch_latest_tickers(exchange_services)

        tickers_df = pandas.DataFrame(list(map(lambda ticker: ticker.to_dict(), tickers_list)))
        tickers_df = tickers_df.astype(dtype={'ask': 'float64', 'bid': 'float64', 'last': 'float64'})

        end_fetch_ticker = time.time()
        print_if_debug_enabled(debug, 'end fetch_latest_tickers: {0} seconds'.format(
            end_fetch_ticker - start_fetch_ticker))
        return tickers_df

    def fetch_tickers_by_pair_name(self, exchange_services):
        """
        :param exchange_services:
        :return: {(str, str): Ticker}
        """
        tickers_list = self.fetch_latest_tickers(exchange_services)
        self.tickers = {}
        for ticker in tickers_list:
            self.tickers[Pair.name_for_base_and_quote(base=ticker.base, quote=ticker.quote)] = ticker
        return self.tickers

    @staticmethod
    def fetch_latest_tickers(exchange_services):
        """
        Args:
            exchange_services dict(int, ExchangeServiceAbc):

        Returns:

        """

        def fetch_for_exchange(exchange_service):
            tickers_list: List[Ticker] = exchange_service.fetch_latest_tickers()
            if tickers_list is not None:
                return tickers_list

        # flatten lists of tickers for each exchange
        return list(itertools.chain.from_iterable(map(fetch_for_exchange, exchange_services.values())))

    @staticmethod
    def fetch_latest_tickers_and_save(exchange_services):
        """
        Fetches latest tickers from exchanges and saves to the database.
        Args:
            exchange_services:
            ticker_dao:
            session:
        Returns session, list: tickers saved to s3
        """
        tickers_list = TickerService.fetch_latest_tickers(exchange_services)
        filepath = write_tickers(env_properties.EnvProperties.env == 'prod', env_properties.S3.output_bucket,
                                 tickers_list)
        return filepath, tickers_list

    @staticmethod
    def set_latest_tickers_from_file(ticker_filename, exchange_services: Dict[int, ExchangeServiceAbc]):
        ticker_df: pandas.DataFrame = pandas.read_csv(ticker_filename)

        ticker_df_grouped: pandas.DataFrame = ticker_df.groupby([
            pandas.Grouper(key='exchange_id'),
            pandas.Grouper(key='app_create_timestamp', freq='min'),
        ])

        for exchange_id, exchange in exchange_services.items():
            latest_tickers_df = ticker_df_grouped.index[]
