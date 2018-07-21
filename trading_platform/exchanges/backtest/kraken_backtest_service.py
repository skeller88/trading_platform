import pandas

from trading_platform.exchanges.backtest.backtest_exchange_service import BacktestExchangeService
from trading_platform.exchanges.data.enums import exchange_names, exchange_ids
from trading_platform.exchanges.data.financial_data import FinancialData


class KrakenBacktestService:
    """
    Uses composition to delegate operations to an instance of BacktestExchangeService. See the BacktestExchangeService docstring for
    details of how that works. The instance exchange_name is set to the exchange_name of this class.
    """
    exchange_name = exchange_names.kraken
    exchange_id = exchange_ids.kraken

    def __init__(self):
        self.__backtest_service = BacktestExchangeService(exchange_id=self.exchange_id, trade_fee=FinancialData(.0026),
                                                  withdrawal_fees=pandas.DataFrame(), echo=False)

    def __getattr__(self, name):
        return getattr(self.__backtest_service, name)
