import ccxt

from exchanges.src.data.enums import exchange_names, exchange_ids
from exchanges.src.data.financial_data import FinancialData
from exchanges.src.live.live_exchange_service import LiveExchangeService

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
        self.client = ccxt.bittrex({
            'apiKey': key,
            'secret': secret
        })
        self.__live_exchange_service = LiveExchangeService(self.exchange_name, self.exchange_id, self.client, key,
                                                           secret,
                                                           trade_fee=FinancialData(.0025),
                                                           withdrawal_fees=withdrawal_fees)

    def __getattr__(self, name):
        return getattr(self.__live_exchange_service, name)
