from trading_platform.exchanges.backtest.backtest_exchange_service import BacktestExchangeService
from trading_platform.exchanges.data.enums import exchange_names, exchange_ids
from trading_platform.exchanges.data.financial_data import FinancialData
from trading_platform.exchanges.withdrawal_fees_service import WithdrawalFeesService


class BittrexBacktestExchangeService:
    """
    Uses composition to delegate operations to an instance of BacktestExchangeService. See the BacktestExchangeService docstring for
    details of how that works. The instance exchange_name is set to the exchange_name of this class.
    """
    exchange_name = exchange_names.bittrex
    exchange_id = exchange_ids.bittrex

    def __init__(self):
        withdrawal_fees = WithdrawalFeesService.by_exchange_ids()[self.exchange_id]
        self.__backtest_service = BacktestExchangeService(exchange_id=self.exchange_id, trade_fee=FinancialData(.0025),
                                                  withdrawal_fees=withdrawal_fees, echo=False)

    def __getattr__(self, name):
        return getattr(self.__backtest_service, name)
