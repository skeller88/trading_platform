import ccxt

from trading_platform.exchanges.data.enums import exchange_names, exchange_ids
from trading_platform.exchanges.data.financial_data import FinancialData
from trading_platform.exchanges.live.live_exchange_service import LiveExchangeService


class KucoinLiveService:
    """
    """
    exchange_id = exchange_ids.kucoin
    exchange_name = exchange_names.kucoin

    def __init__(self, key, secret, withdrawal_fees):
        """
        Args:
            key str:
            secret str:
            withdrawal_fees pandas.DataFrame:
        """
        self.client = ccxt.kucoin({
            'apiKey': key,
            'secret': secret
        })
        self.__live_exchange_service = LiveExchangeService(self.exchange_name, self.exchange_id, self.client, key,
                                                           secret,
                                                           trade_fee=FinancialData(.001),
                                                           withdrawal_fees=withdrawal_fees)

    def __getattr__(self, name):
        return getattr(self.__live_exchange_service, name)