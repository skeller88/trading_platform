"""
nosetests test.services.exchange.backtest.test_backtest_service.TestBacktestService --nocapture
"""
import datetime
import unittest
from copy import deepcopy

import pandas
from nose.tools import eq_, assert_greater, assert_almost_equal

from trading_platform.core.test.data import Defaults, eth_withdrawal_fee
from trading_platform.exchanges.backtest.backtest_service import BacktestService
from trading_platform.exchanges.data.enums import exchange_ids
from trading_platform.exchanges.data.financial_data import one, two, FinancialData, zero
from trading_platform.exchanges.data.pair import Pair
from trading_platform.utils.exceptions import InsufficientFundsException


class TestExchangeServiceSubclassConsistency(unittest.TestCase):
    """
    Using LiveExchangeService to test app logic is difficult. First, the exchanges may take a few seconds to update
    their state, meaning that a test needs to sleep to give the exchange time to catch up. Second, the exchange
    balance state required by each state may vary from test to test, and it's costly and slow to change the exchange
    balance state each time the test suite is run.

    Therefore, BacktestExchangeService is used to test app logic, and LiveExchangeService is used in production.
    So this test makes sure that the return type of BacktestExchangeService matches that of LiveExchangeService.

    The BacktestExchangeService is used to test app logic.
    """
    def setUp(self):
        self.pair = Pair(base='ETH', quote='ARK')
        self.base = self.pair.base
        self.quote = self.pair.quote
        self.initial_base_capital = Defaults.initial_base_capital
        self.initial_ticker = Defaults.initial_ticker
        self.initial_quote_capital = Defaults.initial_quote_capital
        self.trade_fee = Defaults.trade_fee
        self.price = Defaults.initial_ticker

        withdrawal_fees = pandas.DataFrame([
            {
                'currency': self.base,
                'withdrawal_fee': eth_withdrawal_fee
            },
            {
                'currency': self.quote,
                'withdrawal_fee': Defaults.quote_withdrawal_fee
            }
        ])
        withdrawal_fees.set_index('currency', inplace=True)
        self.te = BacktestService(exchange_id=exchange_ids.binance, trade_fee=self.trade_fee,
                                  withdrawal_fees=withdrawal_fees, echo=False)
        self.te.deposit_immediately(self.base, self.initial_base_capital)
        self.te.deposit_immediately(self.quote, self.initial_quote_capital)
        self.te.usdt_tickers = {
            self.pair.base: FinancialData(two)
        }

        self.te.set_buy_prices({
            self.pair.name: self.initial_ticker
        })

        self.completion_timestamp = datetime.datetime.utcnow().timestamp()

