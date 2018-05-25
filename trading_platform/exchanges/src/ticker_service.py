import itertools

from trading_platform.properties.src import env_properties
from trading_platform.storage.src.s3_operations import write_tickers


class TickerService:
    """
    Fetch and save tickers for all exchanges
    """
    @staticmethod
    def fetch_latest_tickers(exchange_services):
        """
        Args:
            exchange_services dict(int, ExchangeServiceAbc):

        Returns:

        """
        def fetch_for_exchange(exchange_service):
            tickers_list = exchange_service.fetch_latest_tickers()
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
        filepath = write_tickers(env_properties.EnvProperties.env == 'prod', env_properties.S3.output_bucket, tickers_list)
        return filepath, tickers_list
