import ccxt

from exchanges.src.data.enums import exchange_names, exchange_ids
from exchanges.src.data.financial_data import FinancialData
from exchanges.src.live.live_exchange_service import LiveExchangeService


class BinanceLiveService:
    """
    Fee info: https://support.binance.com/hc/en-us/articles/115000429332-Fee-Structure-on-Binance
    """
    exchange_id = exchange_ids.binance
    exchange_name = exchange_names.binance

    def __init__(self, key, secret, withdrawal_fees):
        """
        Args:
            key str:
            secret str:
            withdrawal_fees pandas.DataFrame:
        """
        self.client = ccxt.binance({
            'apiKey': key,
            'secret': secret
        })
        self.__live_exchange_service = LiveExchangeService(self.exchange_name, self.exchange_id, self.client, key,
                                                           secret,
                                                           trade_fee=FinancialData(.001),
                                                           withdrawal_fees=withdrawal_fees)

    def __getattr__(self, name):
        return getattr(self.__live_exchange_service, name)
