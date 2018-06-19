import os

import ccxt

from trading_platform.exchanges.data.enums import exchange_names, exchange_ids
from trading_platform.exchanges.data.enums.order_side import OrderSide
from trading_platform.exchanges.data.financial_data import FinancialData
from trading_platform.exchanges.data.order import Order
from trading_platform.exchanges.live.live_exchange_service import LiveExchangeService

# Markets

MARKETS = [
    'USDT-BTC',
    'USDT-BCC',
    'USDT-NEO',
    'USDT-OMG',
    'USDT-LTC',
    'USDT-ETH',
    'USDT-XRP',
    'USDT-ZEC',
    'USDT-XMR',
    'USDT-BTG',
    'USDT-ETC',
    'USDT-DASH',

    'BTC-NEO',
    'BTC-OMG',
    'BTC-LTC',
    'BTC-ETH',
    'BTC-XRP',
    'BTC-ZEC',
    'BTC-XMR',
    'BTC-BTG',
    'BTC-ETC',
    'BTC-DASH',
]


class BittrexLiveService:
    """
    Documentation: https://bittrex.com/home/api
    # Fee info: https://support.bittrex.com/hc/en-us/articles/115000199651-What-fees-does-Bittrex-charge-
    """
    exchange_id = exchange_ids.bittrex
    exchange_name = exchange_names.bittrex

    def __init__(self, key, secret, withdrawal_fees):
        """
        Args:
            key str:
            secret str:
            withdrawal_fees pandas.DataFrame:
        """
        self.__client = ccxt.bittrex({
            'apiKey': key,
            'secret': secret
        })
        self.__live_exchange_service = LiveExchangeService(self.exchange_name, self.exchange_id, self.__client, key,
                                                           secret,
                                                           trade_fee=FinancialData(.0025),
                                                           withdrawal_fees=withdrawal_fees)

    def __getattr__(self, name):
        return getattr(self.__live_exchange_service, name)

    def create_conditional_order(self, order_side, pair, amount, target, condition_type):
        """
        This method currently returns a 500. Not sure if it's fixable because this method is only exposed
        via the web API.
        https://github.com/ccxt/ccxt/issues/2889

        Args:
            order_side:
            pair:
            amount:
            price:
            **params:

        Returns:

        """
        # Bittrex integration expects floats
        amount = float(amount)

        self.__client.verbose = True
        # auth/market/TradeSell
        # pub/markets/GetMarketSummaries
        suffix = 'TradeBuy' if order_side == OrderSide.buy else 'TradeSell'
        # {'url': 'https://bittrex.com/api/v2.0/pub/auth/market/TradeSell', 'method': 'POST', 'body': None, 'headers': None}
        params = {
            'MarketName': '{0}-{1}'.format(pair.base, pair.quote),
            'OrderType': 'LIMIT',
            'Quantity': amount,
            'Rate': target,
            'ConditionType': condition_type,
            'TimeInEffect': 'GOOD_TIL_CANCELLED',
            'Target': target
        }
        url: str = self.get_url(os.path.join('auth/market', suffix), params)
        response = self.__client.fetch(url, 'POST', headers=None, body=None)
        # response = make_api_request(self.__client.fetch, url, 'POST')

        self.__client.verbose = False
        if response is None:
            return

        return Order.from_fetch_order_response(response, self.exchange_id)

    def get_url(self, path, params) -> str:
        """
        Taken from ccxt.
        Args:
            path:
            api:
            method:
            params:
            headers:
            body:

        Returns:

        """
        url = 'https://bittrex.com/api/v2.0/'
        url += path
        if params:
            url += '?' + self.__client.urlencode(params)
        return url