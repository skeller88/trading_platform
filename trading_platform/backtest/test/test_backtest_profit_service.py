import os
import unittest
from functools import reduce

import pandas
from nose.tools import eq_, assert_almost_equal, assert_true

from trading_platform.backtest.backtest_profit_service import BacktestProfitService
from trading_platform.core.test.data import Defaults

from trading_platform.exchanges.data.enums import exchange_ids
from trading_platform.exchanges.data.financial_data import FinancialData, zero, one
from trading_platform.exchanges.data.pair import Pair
from trading_platform.exchanges.backtest.backtest_service import BacktestService


class ProfitServiceTest(unittest.TestCase):
    def setUp(self):
        self.pair = Pair(base='ETH', quote='ARK')
        self.base = self.pair.base
        self.quote = self.pair.quote
        quote_ticker = one
        self.initial_base_capital = FinancialData(20)
        self.initial_tickers = {
            self.quote: quote_ticker,
            self.base: one
        }
        self.initial_quote_capital = FinancialData(20)
        self.trade_fee = zero

        withdrawal_fees = {
            self.base: FinancialData(.008),
            self.quote: FinancialData(.002)
        }

        self.he = BacktestService(exchange_id=exchange_ids.bittrex, trade_fee=self.trade_fee, withdrawal_fees=withdrawal_fees,
                                  echo=False)

        self.le = BacktestService(exchange_id=exchange_ids.binance, trade_fee=self.trade_fee, withdrawal_fees=withdrawal_fees,
                                  echo=False)

        self.he.deposit_immediately(self.quote, self.initial_quote_capital)
        self.le.deposit_immediately(self.base, self.initial_base_capital)

        self.he.buy_prices = {
            self.pair.quote: quote_ticker
        }

        self.profit_service = BacktestProfitService(Defaults.income_tax, Defaults.ltcg_tax, self.he, self.le,
                                                    self.initial_tickers)

    def test_init(self):
        eq_(len(self.profit_service.profit_snapshots), 0)
        eq_(self.profit_service.income_tax, Defaults.income_tax)
        eq_(self.profit_service.ltcg_tax, Defaults.ltcg_tax)
        eq_(self.profit_service.initial_tickers, self.initial_tickers)

    def test_balances_across_exchanges(self):
        balances = self.profit_service.balances_across_exchanges()
        for currency in balances.keys():
            eq_(balances[currency],
                self.profit_service.he.get_balance(currency) + self.profit_service.le.get_balance(currency))

    def test_zero_net_profits(self):
        """
        With no profits, the bh and arb net profits should be the same.
        :return:
        """
        start_balance = self.profit_service.balances_across_exchanges()
        arb_net_profits, bh_net_profits = self.profit_service.net_profits(start_balance, self.initial_tickers)
        assert_almost_equal(zero, arb_net_profits, places=14)
        assert_almost_equal(zero, bh_net_profits, places=14)

    def test_positive_net_profits(self):
        """
        With the same positive gross profits due to capital gains, bh net profits should be > arb net profits because
        arb profits are taxed at a higher rate.
        :return:
        """
        start_balance = self.profit_service.balances_across_exchanges()
        gain = FinancialData(.02)
        end_tickers = {
            self.base: one,
            self.quote: self.initial_tickers[self.quote] * (one + gain)
        }
        self.he.capital_gains = gain * (self.he.get_balance(self.quote) + self.le.get_balance(self.quote))
        assert_almost_equal(self.he.capital_gains, FinancialData(.4), places=FinancialData.five_places)

        arb_net_profits, bh_net_profits = self.profit_service.net_profits(start_balance, end_tickers)
        assert_almost_equal(arb_net_profits, FinancialData(136.80), places=2)
        assert_almost_equal(bh_net_profits, FinancialData(184.80), places=2)

    def test_negative_net_profits(self):
        """
        With the same positive gross profits due to capital gains, bh net profits should be > arb net profits because
        arb profits are taxed at a higher rate.
        :return:
        """
        start_balance = self.profit_service.balances_across_exchanges()
        gain = FinancialData(-.02)
        end_tickers = {
            self.base: one,
            self.quote: self.initial_tickers[self.quote] * (one + gain)
        }
        self.he.capital_losses = abs(gain * (self.he.get_balance(self.quote) + self.le.get_balance(self.quote)))
        assert_almost_equal(self.he.capital_losses, FinancialData(.4), places=FinancialData.five_places)

        arb_net_profits, bh_net_profits = self.profit_service.net_profits(start_balance, end_tickers)
        assert_almost_equal(arb_net_profits, FinancialData(-240.00), places=2)
        assert_almost_equal(bh_net_profits, FinancialData(-240.00), places=2)

    def test_save_profit_history(self):
        """
        Should save a dataframe with one column for each of the currency balances being tracked, and "alpha" and
        "arb_profit" columns. For example:
                 ARK  ETH  alpha  profits
        0  29.161339   20   0.000000      0.00000
        1  58.322677   20   0.520606     20.82425
        Returns:

        """
        num_currencies_tracked = len(self.initial_tickers.keys())
        # quote and base currencies
        eq_(num_currencies_tracked, 2)
        self.profit_service.create_profit_snapshot(self.initial_tickers)
        gain = FinancialData(.2)
        end_tickers = {currency: ticker * (one + gain) for currency, ticker in self.initial_tickers.items()}

        self.he.deposit_immediately(self.quote, self.initial_quote_capital)
        self.he.capital_gains = reduce(lambda total_gain, currency: gain * self.he.get_balance(currency),
                                       self.he.fetch_balances(), zero)
        self.le.capital_gains = reduce(lambda total_gain, currency: gain * self.le.get_balance(currency),
                                       self.he.fetch_balances(), zero)
        self.profit_service.create_profit_snapshot(end_tickers)
        dest_path = os.path.join(os.getcwd(), 'test.csv')
        self.profit_service.save_profit_history(dest_path)
        tdf = pandas.read_csv(dest_path)
        eq_(len(tdf), 2)
        # number of currencies tracked across all exchanges
        eq_(len(tdf.columns), len(BacktestProfitService.columns) + num_currencies_tracked)
        for currency in self.initial_tickers.keys():
            assert_true(currency in tdf.columns)
        os.remove(dest_path)