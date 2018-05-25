import ccxt

from trading_platform.exchanges.src.data.enums import exchange_names, exchange_ids
from trading_platform.exchanges.src.data.financial_data import FinancialData
from trading_platform.exchanges.src.live.live_exchange_service import LiveExchangeService


class KrakenLiveService:
    """
    https://www.kraken.com/help/fees
    """
    exchange_name = exchange_names.kraken
    exchange_id = exchange_ids.kraken

    def __init__(self, key, secret, withdrawal_fees):
        self.client = ccxt.kraken({
            'apiKey': key,
            'secret': secret
        })
        self.__live_exchange_service = LiveExchangeService(self.exchange_name, self.exchange_id, self.client, key,
                                                           secret, trade_fee=FinancialData(.0026),
                                                           withdrawal_fees=withdrawal_fees)

    def __getattr__(self, name):
        return getattr(self.__live_exchange_service, name)
