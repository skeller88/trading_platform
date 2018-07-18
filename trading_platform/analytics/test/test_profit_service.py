import os
import unittest
from copy import copy

import pandas
from nose.tools import assert_greater, assert_less, eq_, assert_true

from trading_platform.analytics.profit_service import ProfitService
from trading_platform.core.test.data import Defaults
from trading_platform.exchanges.backtest import backtest_subclasses
from trading_platform.exchanges.data.enums import exchange_ids
from trading_platform.exchanges.data.financial_data import FinancialData, zero, one, two
from trading_platform.exchanges.data.pair import Pair
from trading_platform.exchanges.data.ticker import Ticker
from trading_platform.exchanges.ticker_service import TickerService


class TestBacktestProfitService(unittest.TestCase):
    @classmethod
    def setUp(cls):
        cls.exchanges_by_id = backtest_subclasses.instantiate()
        cls.quote_pair = Pair(base='ETH', quote='ARK')
        cls.base = cls.quote_pair.base
        cls.quote = cls.quote_pair.quote
        cls.btc_usdt_pair = Pair(base='USDT', quote='BTC')
        cls.eth_usdt_pair = Pair(base='USDT', quote='ETH')
        cls.initial_tickers = {
            # https://www.coingecko.com/en/price_charts/ark/eth
            cls.quote_pair.name: Ticker(base=cls.quote_pair.base, quote=cls.quote_pair.quote,
                                           bid=FinancialData(.0015)),
            cls.btc_usdt_pair.name: Ticker(base=cls.btc_usdt_pair.base, quote=cls.btc_usdt_pair.quote,
                                           bid=FinancialData(5000)),
            cls.eth_usdt_pair.name: Ticker(base=cls.eth_usdt_pair.base, quote=cls.eth_usdt_pair.quote,
                                           bid=FinancialData(400)),
        }
        cls.end_tickers = cls.initial_tickers

        cls.initial_usd_value = FinancialData(10000)
        cls.ticker_service = TickerService()

        cls.exchanges_by_id[exchange_ids.bittrex].set_tickers(cls.initial_tickers)
        cls.initial_base_capital = cls.initial_usd_value / cls.initial_tickers.get(cls.eth_usdt_pair.name).bid / two
        cls.exchanges_by_id[exchange_ids.bittrex].deposit_immediately(cls.base, cls.initial_base_capital)

        cls.exchanges_by_id[exchange_ids.binance].set_tickers(cls.initial_tickers)
        cls.initial_quote_capital = cls.initial_base_capital / cls.initial_tickers.get(cls.quote_pair.name).bid
        cls.exchanges_by_id[exchange_ids.binance].deposit_immediately(cls.quote, cls.initial_quote_capital)

    def test_init(self):
        profit_service = ProfitService(initial_tickers=self.initial_tickers, exchanges_by_id=self.exchanges_by_id)
        eq_(len(profit_service.profit_history), 1)
        eq_(profit_service.income_tax, Defaults.income_tax)
        eq_(profit_service.ltcg_tax, Defaults.ltcg_tax)
        eq_(profit_service.initial_tickers, self.initial_tickers)

    def test_balance_usdt_value(self):
        profit_service = ProfitService(initial_tickers=self.initial_tickers, exchanges_by_id=self.exchanges_by_id)
        usd_value = profit_service.exchange_balances_usdt_value(self.exchanges_by_id, self.initial_tickers)
        # Since tickers are always changing and exchange balances will change, the best we can do
        # is assert greater than zero, and verify manually that the total balance is what's expected.
        assert_greater(usd_value, zero)

    def test_profit_summary_end_balance_equals_start_balance(self):
        profit_service = ProfitService(initial_tickers=self.initial_tickers, exchanges_by_id=self.exchanges_by_id)
        profit_summary = profit_service.profit_summary(self.initial_tickers)
        eq_(profit_summary.get('gross_profits'), zero)
        eq_(profit_summary.get('bh_taxes'), profit_summary.get('taxes'))

        eq_(profit_summary.get('bh_gross_profits'), zero)
        eq_(profit_summary.get('bh_gross_profits'), profit_summary.get('gross_profits'))
        eq_(profit_summary.get('bh_net_profits'), profit_summary.get('net_profits'))
        eq_(profit_summary.get('bh_return'), profit_summary.get('strat_return'))

        eq_(profit_summary.get('alpha'), zero)
        eq_(profit_summary.get('net_profits_over_bh'), zero)

    def test_profit_summary_gains_ticker_increase(self):
        """
        end quote ticker > initial quote ticker and therefore end_balance_usdt_value > start_balance_usdt_value.
        Therefore, strat_return > bh_return.

        Returns:

        """
        ps = ProfitService(initial_tickers=self.initial_tickers, exchanges_by_id=self.exchanges_by_id)
        end_quote_ticker: Ticker = self.initial_tickers.get(self.quote_pair.name)
        end_quote_ticker.bid = end_quote_ticker.bid * FinancialData(1.5)
        self.end_tickers[self.quote_pair.name] = end_quote_ticker

        profit_summary = ps.profit_summary(self.end_tickers)
        for field in ps.profit_summary_fields:
            assert(profit_summary.get(field) is not None)

        assert_greater(profit_summary.get('gross_profits'), zero)
        # BTC ticker doesn't change
        eq_(profit_summary.get('bh_taxes'), profit_summary.get('taxes'))

        eq_(profit_summary.get('bh_gross_profits'), zero)
        assert_greater(profit_summary.get('gross_profits'), profit_summary.get('bh_gross_profits'))
        assert_greater(profit_summary.get('net_profits'), profit_summary.get('bh_net_profits'))
        assert_greater(profit_summary.get('strat_return'), profit_summary.get('bh_return'))

        assert_greater(profit_summary.get('alpha'), zero)
        assert_greater(profit_summary.get('net_profits_over_bh'), zero)

    def test_profit_summary_gains_amount_increase(self):
        """
        end quote amount > initial quote amount and so end_balance_usdt_value > start_balance_usdt_value.
        Therefore, strat_return > bh_return.

        Returns:

        """
        ps = ProfitService(initial_tickers=self.initial_tickers, exchanges_by_id=self.exchanges_by_id)
        self.exchanges_by_id[exchange_ids.binance].deposit_immediately(self.quote_pair.quote, FinancialData(50))
        profit_summary = ps.profit_summary(self.end_tickers)
        for field in ps.profit_summary_fields:
            assert(profit_summary.get(field) is not None)

        assert_greater(profit_summary.get('gross_profits'), zero)
        # BTC ticker doesn't change
        eq_(profit_summary.get('bh_taxes'), profit_summary.get('taxes'))

        eq_(profit_summary.get('bh_gross_profits'), zero)
        assert_greater(profit_summary.get('gross_profits'), profit_summary.get('bh_gross_profits'))
        assert_greater(profit_summary.get('net_profits'), profit_summary.get('bh_net_profits'))
        assert_greater(profit_summary.get('strat_return'), profit_summary.get('bh_return'))

        assert_greater(profit_summary.get('alpha'), zero)
        assert_greater(profit_summary.get('net_profits_over_bh'), zero)

    def test_save_profit_history(self):
        """
        Should save a dataframe with one column for each of the currency balances being tracked, and "alpha" and
        "arb_profit" columns. For example:
                 ARK  ETH  alpha  profits
        0  29.161339   20   0.000000      0.00000
        1  58.322677   20   0.520606     20.82425
        Returns:

        """
        profit_service = ProfitService(initial_tickers=self.initial_tickers, exchanges_by_id=self.exchanges_by_id)
        profit_service.profit_summary(self.end_tickers)

        dest_path = os.path.join(os.getcwd(), 'test.csv')
        profit_service.save_profit_history(dest_path)
        tdf = pandas.read_csv(dest_path)
        eq_(len(tdf), 2)
        for field in ProfitService.profit_summary_fields:
            assert_true(field in tdf.columns)
        os.remove(dest_path)