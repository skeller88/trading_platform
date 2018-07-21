"""
These exchange services are used in backtests. They use in-memory data structures to maintain balance and order state
while stub exchange operations such as buying, selling, and fetching balances. They fetch ticker data from csv files.
"""
from trading_platform.exchanges.backtest.binance_backtest_service import BinanceBacktestService
from trading_platform.exchanges.backtest.bittrex_backtest_service import BittrexBacktestService
from trading_platform.exchanges.backtest.gdax_backtest_service import GdaxBacktestService
from trading_platform.exchanges.backtest.kraken_backtest_service import KrakenBacktestService
from trading_platform.exchanges.backtest.kucoin_backtest_service import KucoinBacktestService
from trading_platform.exchanges.backtest.poloniex_backtest_service import PoloniexBacktestService
from trading_platform.exchanges.data.enums import exchange_ids


def instantiate():
    """
    https://stackoverflow.com/questions/3862310/how-can-i-find-all-subclasses-of-a-class-given-its-name doesn't
    work if the variables aren't declared in local scope. So declare manually.
    :return:
    """
    return {
        exchange_ids.binance: BinanceBacktestService(),
        exchange_ids.bittrex: BittrexBacktestService(),
        exchange_ids.gdax: GdaxBacktestService(),
        exchange_ids.kraken: KrakenBacktestService(),
        exchange_ids.kucoin: KucoinBacktestService(),
        exchange_ids.poloniex: PoloniexBacktestService()
    }