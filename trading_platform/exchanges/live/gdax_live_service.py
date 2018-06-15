from typing import List, Dict, Optional

import ccxt

from trading_platform.exchanges.data.enums import exchange_names, exchange_ids
from trading_platform.exchanges.data.financial_data import FinancialData
from trading_platform.exchanges.data.pair import Pair
from trading_platform.exchanges.data.ticker import Ticker
from trading_platform.exchanges.live.live_exchange_service import LiveExchangeService
from trading_platform.utils.http_utils import make_api_request

GDAX_API_BASE_URL = 'https://api.gdax.com'
# Markets
MARKETS = [
    'BCH/USD',
    'BTC/USD',
    'ETH/USD',
    'ETH/BTC',
    'LTC/BTC',
    'LTC/USD'
]


class GdaxLiveService():
    """
    Fee info: https://docs.gdax.com/#fees
    """
    exchange_id = exchange_ids.gdax
    exchange_name = exchange_names.gdax

    def __init__(self, key, secret, withdrawal_fees):
        """
        Args:
            key str:
            secret str:
            withdrawal_fees pandas.DataFrame:
        """
        self.client = ccxt.gdax({
            'apiKey': key,
            'secret': secret
        })
        self.__live_exchange_service = LiveExchangeService(self.exchange_name, self.exchange_id, self.client, key,
                                                           secret,
                                                           trade_fee=FinancialData(.0025),
                                                           withdrawal_fees=withdrawal_fees)
        self.__tickers = {}

    def __getattr__(self, name):
        return getattr(self.__live_exchange_service, name)

    ###########################################
    # Market state
    ###########################################

    def fetch_latest_tickers(self) -> List[Ticker]:
        """
        "ticker" gets updated by multiple threads. Built in types are inherently thread-safe:
        https://docs.python.org/3/glossary.html#term-global-interpreter-lock
        Ideally side effects wouldn't be used, but it works for now.

        Can't use multithreading for now because it causes rate-limiting from GDAX.

        Returns list<Ticker>:
        """
        self.__tickers = {}
        tickers: List[Ticker] = []
        for market in MARKETS:
            ticker = self.fetch_ticker(market)
            if ticker is None or ticker.base is None or ticker.quote is None:
                continue
            self.__tickers[Pair(base=ticker.base, quote=ticker.quote).name] = ticker
            tickers.append(ticker)

        return tickers

    def fetch_distinct_tickers(self, start_date, end_date, data_operation_config):
        pass

    def fetch_ticker(self, market):
        ticker = make_api_request(self.client.fetch_ticker, market)

        pair_name, ticker_instance = Ticker.from_exchange_data(ticker, self.exchange_id, Ticker.current_version)
        if ticker_instance is None:
            return

        return ticker_instance

    def get_tickers(self) -> Dict[str, Ticker]:
        """
        LiveExchangeService implements this function, but since GdaxLiveService is implementing fetch_tickers,
        it won't have access to LiveExchangeService.__tickers.

        Returns:

        """
        return self.__tickers

    def get_ticker(self, pair_name) -> Optional[Ticker]:
        return self.__tickers.get(pair_name)

    def fetch_order_book(self, symbol, limit=None, params={}):
        return self.order_book(symbol=symbol, limit=limit, params=params)

    def order_book(self, product_id, level=1):
        """
        Args:
            product_id:
            level:

        Returns:
        Market Data: https://docs.gdax.com/?python#market-data
        {
            "sequence": "3",
            "bids": [
                [ price, size, exchange_order_id ],
                [ "295.96","0.05088265","3b0f1225-7f84-490b-a29f-0faef9de823a" ],
                ...
            ],
            "asks": [
                [ price, size, exchange_order_id ],
                [ "295.97","5.72036512","da863862-25f4-4868-ac41-005d11ab0a5f" ],
                ...
            ]
        }
        """
        pass
        # return self.get('products/{0}/book'.format(product_id), **{'level': level})
