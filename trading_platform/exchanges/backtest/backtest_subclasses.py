"""
These exchange services are used in backtests. They use in-memory data structures to maintain balance and order state
while stub exchange operations such as buying, selling, and fetching balances. They fetch ticker data from csv files.
"""
from trading_platform.exchanges.backtest.binance_backtest_service import BinanceBacktestExchangeService
from trading_platform.exchanges.backtest.bittrex_backtest_service import BittrexBacktestExchangeService
from trading_platform.exchanges.data.enums import exchange_ids


def instantiate():
    """
    https://stackoverflow.com/questions/3862310/how-can-i-find-all-subclasses-of-a-class-given-its-name doesn't
    work if the variables aren't declared in local scope. So declare manually.
    :return:
    """
    return {
        exchange_ids.binance: BinanceBacktestExchangeService(),
        exchange_ids.bittrex: BittrexBacktestExchangeService()
    }