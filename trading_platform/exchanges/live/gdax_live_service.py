from typing import Dict

import ccxt

import trading_platform.utils.api_request_msgs as api_request_msgs
from trading_platform.core.constants import exchange_pairs
from trading_platform.exchanges.data.balance import Balance
from trading_platform.exchanges.data.enums import exchange_names, exchange_ids
from trading_platform.exchanges.data.order import Order
from trading_platform.exchanges.data.pair import Pair
from trading_platform.exchanges.data.ticker import Ticker
from trading_platform.exchanges.exchange_service_abc import ExchangeServiceAbc
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


class GdaxLiveService(ExchangeServiceAbc):
    """
    Fee info: https://docs.gdax.com/#fees
    """
    exchange_name = exchange_names.gdax
    exchange_id = exchange_ids.gdax

    def __init__(self, key, secret, withdrawal_fees):
        super().__init__(key=key, secret=secret, trade_fee=.0025)
        self.client = ccxt.gdax({
            'apiKey': key,
            'secret': secret
        })
        self.__tickers = {}

    ###########################################
    # Trading - Orders
    ###########################################

    def cancel_order(self, order_id, market, params={}):
        self.client.cancel_order(order_id, market, params)

    def create_limit_buy_order(self, symbol, amount, price, *params):
        return self.client.create_limit_buy_order(symbol, amount, price, params)

    def create_limit_sell_order(self, symbol, amount, price, *params):
        return self.client.create_limit_sell_order(symbol, amount, price, params)

    ###########################################
    # Account state
    ###########################################

    def get_balance(self, currency):
        pass

    def fetch_balances(self) -> Dict[str, Balance]:
        """
        example API response:
        {'info': [{'Currency': 'BTC', 'Balance': 0.0, 'Available': 0.0, 'Pending': 0.0, 'CryptoAddress': '1FdGHn9b9dzwfEfxnjK4DJoy45DnqzaQcF'}, ...]}
        :return:
        """
        data = make_api_request(api_request_msgs.BALANCE_ERR.format(self.name()), self.client.fetch_balance)

        if data is None:
            return

        return {
            balance.get('Currency'): {
                'free': balance.get('Available'),
                'pending': balance.get('Pending'),
                'balance': balance.get('Balance')
            } for balance in data.get('info') if balance.get('Currency') is not None
        }

    def fetch_closed_orders(self):
        self.client.load_markets()
        return make_api_request(
            api_request_msgs.OPEN_ORDERS_ERR.format(self.name()), self.client.fetch_closed_orders)

    def fetch_market_symbols(self):
        # self.client.load_markets()
        # return self.client.markets.keys()
        return exchange_pairs.gdax

    def fetch_open_orders(self, symbol=None):
        order_data_list = make_api_request(
            api_request_msgs.OPEN_ORDERS_ERR.format(exchange_names.poloniex), self.client.fetch_open_orders,
            symbol)

        return [Order(**order_data) for order_data in order_data_list] \
            if order_data_list is not None else []

    ###########################################
    # Trading - Funding
    ###########################################

    def fetch_deposit_destination(self, currency, params):
        pass

    def withdraw(self, currency, amount, address, tag=None, params={}):
        pass

    def withdraw_all(self, currency, address, tag=None, params={}):
        pass
    ###########################################
    # Market state
    ###########################################

    def fetch_latest_tickers(self):
        """
        "ticker" gets updated by multiple threads. Built in types are inherently thread-safe:
        https://docs.python.org/3/glossary.html#term-global-interpreter-lock
        Ideally side effects wouldn't be used, but it works for now.

        Can't use multithreading for now because it causes rate-limiting from GDAX.

        Returns list<Ticker>:
        """
        self.__tickers = {}
        tickers = []
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
        ticker = make_api_request(
            api_request_msgs.TICKER_ERR.format(self.name()), self.client.fetch_ticker, market)

        pair_name, ticker_instance = Ticker.from_exchange_data(ticker, self.id(), Ticker.current_version)
        if ticker_instance is None:
            return

        return ticker_instance

    def get_tickers(self):
        return self.__tickers

    def get_ticker(self, pair_name):
        return self.__tickers.get(pair_name)

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
                [ price, size, order_id ],
                [ "295.96","0.05088265","3b0f1225-7f84-490b-a29f-0faef9de823a" ],
                ...
            ],
            "asks": [
                [ price, size, order_id ],
                [ "295.97","5.72036512","da863862-25f4-4868-ac41-005d11ab0a5f" ],
                ...
            ]
        }
        """
        pass
        # return self.get('products/{0}/book'.format(product_id), **{'level': level})

    @staticmethod
    def id():
        return exchange_ids.gdax

    @staticmethod
    def name():
        return exchange_names.gdax