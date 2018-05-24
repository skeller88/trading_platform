import ccxt

from exchanges.src.data.enums import exchange_names, exchange_ids
from exchanges.src.data.financial_data import FinancialData
from exchanges.src.live.live_exchange_service import LiveExchangeService


class PoloniexLiveService:
    """
    https://poloniex.com/fees/
    """
    exchange_name = exchange_names.poloniex
    exchange_id = exchange_ids.poloniex

    def __init__(self, key, secret, withdrawal_fees):
        self.client = CustomCcxtPoloniex({
            'apiKey': key,
            'secret': secret
        })
        self.__live_exchange_service = LiveExchangeService(self.exchange_name, self.exchange_id, self.client, key,
                                                           secret,
                                                           trade_fee=FinancialData(.0025),
                                                           withdrawal_fees=withdrawal_fees)

    def __getattr__(self, name):
        return getattr(self.__live_exchange_service, name)


class CustomCcxtPoloniex(ccxt.poloniex):
    """
    Using default milliseconds value results in nonce errors.
    https://github.com/ccxt/ccxt/wiki/Manual#overriding-the-nonce
    """
    def nonce(self):
        return self.microseconds()
