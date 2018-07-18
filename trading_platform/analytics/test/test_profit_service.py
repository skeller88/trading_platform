import os
import unittest

import pandas
from copy import copy

from nose.tools import assert_greater, assert_less, eq_, assert_true

from trading_platform.analytics.profit_service import ProfitService
from trading_platform.core.test.data import Defaults
from trading_platform.exchanges.backtest import backtest_subclasses
from trading_platform.exchanges.data.enums import exchange_ids
from trading_platform.exchanges.data.financial_data import FinancialData, zero, one_hundred, one, two
from trading_platform.exchanges.data.pair import Pair
from trading_platform.exchanges.data.ticker import Ticker
from trading_platform.exchanges.ticker_service import TickerService
from trading_platform.storage.daos.balance_dao import BalanceDao


class TestBacktestProfitService(unittest.TestCase):
    @classmethod
    def setUp(cls):
        cls.exchange_services = backtest_subclasses.instantiate()
        cls.quote_pair = Pair(base='ETH', quote='ARK')
        cls.base = cls.quote_pair.base
        cls.quote = cls.quote_pair.quote
        cls.btc_usdt_pair = Pair(base='USDT', quote='BTC')
        cls.eth_usdt_pair = Pair(base='USDT', quote='ETH')
        # https://www.coingecko.com/en/price_charts/ark/eth
        cls.quote_ticker = FinancialData(.0013)
        cls.initial_tickers = {
            cls.quote_pair.name: Ticker(base=cls.quote_pair.base, quote=cls.quote_pair.quote,
                                           bid=FinancialData(.0015)),
            cls.btc_usdt_pair.name: Ticker(base=cls.btc_usdt_pair.base, quote=cls.btc_usdt_pair.quote,
                                           bid=FinancialData(5000)),
            cls.eth_usdt_pair.name: Ticker(base=cls.eth_usdt_pair.base, quote=cls.eth_usdt_pair.quote,
                                           bid=FinancialData(400)),
        }

        cls.initial_usd_value = FinancialData(10000)
        cls.ticker_service = TickerService()
        cls.kwargs = {
            'balance_dao': BalanceDao(),
            'ticker_service': cls.ticker_service,
            'start_balance_usdt_value': cls.initial_usd_value,
            'initial_tickers': cls.initial_tickers
        }

        cls.exchange_services[exchange_ids.bittrex].set_tickers(cls.initial_tickers)
        cls.initial_base_capital = cls.initial_usd_value / cls.initial_tickers.get(cls.eth_usdt_pair.name).bid / two
        cls.exchange_services[exchange_ids.bittrex].deposit_immediately(cls.base, cls.initial_base_capital)

        cls.exchange_services[exchange_ids.binance].set_tickers(cls.initial_tickers)
        cls.initial_quote_capital = cls.initial_base_capital / cls.initial_tickers.get(cls.quote_pair.name).bid
        cls.exchange_services[exchange_ids.binance].deposit_immediately(cls.quote, cls.initial_quote_capital)

        # must be called after .set_tickers()
        cls.end_tickers = cls.ticker_service.fetch_tickers_by_pair_name(cls.exchange_services)

    def test_init(self):
        profit_service = ProfitService(**self.kwargs)
        eq_(len(profit_service.profit_history), 0)
        eq_(profit_service.income_tax, Defaults.income_tax)
        eq_(profit_service.ltcg_tax, Defaults.ltcg_tax)
        eq_(profit_service.initial_tickers, self.initial_tickers)

    def test_balance_usdt_value(self):
        profit_service = ProfitService(**self.kwargs)
        usd_value = profit_service.exchange_balances_usdt_value(self.exchange_services, self.end_tickers)
        # Since tickers are always changing and exchange balances will change, the best we can do
        # is assert greater than zero, and verify manually that the total balance is what's expected.
        assert_greater(usd_value, zero)

    def test_profit_summary_end_balance_equals_start_balance(self):
        profit_service = ProfitService(**self.kwargs)
        profit_summary = profit_service.profit_summary(self.exchange_services, self.end_tickers)
        eq_(profit_summary.get('gross_profits'), zero)
        eq_(profit_summary.get('bh_taxes'), profit_summary.get('taxes'))

        eq_(profit_summary.get('bh_gross_profits'), zero)
        eq_(profit_summary.get('bh_gross_profits'), profit_summary.get('gross_profits'))
        eq_(profit_summary.get('bh_net_profits'), profit_summary.get('net_profits'))
        eq_(profit_summary.get('bh_return'), profit_summary.get('strat_return'))

        eq_(profit_summary.get('alpha'), zero)
        eq_(profit_summary.get('net_profits_over_bh'), zero)

    def test_profit_summary_end_balance_less_than_start_balance(self):
        """
        Assert that the profit summary has all of the expected fields, and that their values are approximately
        what would be expected.

        The following test assumes that the current usd value of all exchange balances is << start_balance_usdt_value of
        10000, and that btc has significantly increased in value. in other words, high losses on the strategy
        strategy, and high gains on buy and hold. In this case, bh_taxes > taxes, bh_return >> strat_return,
        and gross_profits < 0.

        Returns:

        """
        ps = ProfitService(**self.kwargs)
        end_btc_ticker = copy(self.kwargs['initial_tickers'].get(self.btc_usdt_pair.name))
        end_btc_ticker.bid = end_btc_ticker.bid * FinancialData(1.5)
        self.end_tickers[self.btc_usdt_pair.name] = end_btc_ticker

        end_quote_ticker = copy(self.kwargs['initial_tickers'].get(self.quote_pair.name))
        end_quote_ticker.bid = end_quote_ticker.bid * FinancialData(.01)
        self.end_tickers[self.quote_pair.name] = end_quote_ticker

        profit_summary = ps.profit_summary(self.exchange_services, self.end_tickers)
        for field in ps.profit_summary_fields:
            assert(profit_summary.get(field) is not None)

        assert_less(profit_summary.get('gross_profits'), zero)
        assert_greater(profit_summary.get('bh_taxes'), profit_summary.get('taxes'))

        assert_greater(profit_summary.get('bh_gross_profits'), zero)
        assert_greater(profit_summary.get('bh_gross_profits'), profit_summary.get('gross_profits'))
        assert_greater(profit_summary.get('bh_net_profits'), profit_summary.get('net_profits'))
        assert_greater(profit_summary.get('bh_return'), profit_summary.get('strat_return'))

        assert_less(profit_summary.get('alpha'), zero)
        assert_less(profit_summary.get('net_profits_over_bh'), zero)

    def test_profit_summary_end_balance_greater_than_start_balance(self):
        """
         Assert that the profit summary has all of the expected fields, and that their values are approximately
        what would be expected.

        The following test assumes that the current usd value of all exchange balances is >> start_balance_usdt_value of
        50, and that btc has decreased in value. in other words, high gains on the strategy
        strategy, and high losses on buy and hold. In this case, taxes > bh_taxes, strat_return >> bh_return,
        and gross_profits > 0.

        Returns:

        """
        self.kwargs['start_balance_usdt_value'] = FinancialData(50)
        ps = ProfitService(**self.kwargs)
        end_btc_ticker = copy(self.kwargs['initial_tickers'].get(self.btc_usdt_pair.name))
        end_btc_ticker.bid = end_btc_ticker.bid * (one - FinancialData(.1))
        self.end_tickers[self.btc_usdt_pair.name] = end_btc_ticker
        profit_summary = ps.profit_summary(self.exchange_services, self.end_tickers)
        print(profit_summary)
        for field in ps.profit_summary_fields:
            assert(profit_summary.get(field) is not None)

        assert_less(profit_summary.get('bh_gross_profits'), zero)
        assert_greater(profit_summary.get('gross_profits'), zero)
        assert_greater(profit_summary.get('taxes'), profit_summary.get('bh_taxes'))
        assert_less(profit_summary.get('bh_gross_profits'), profit_summary.get('gross_profits'))
        assert_less(profit_summary.get('bh_net_profits'), profit_summary.get('net_profits'))
        assert_less(profit_summary.get('bh_return'), profit_summary.get('strat_return'))

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
        profit_service = ProfitService(**self.kwargs)
        profit_service.profit_summary(self.exchange_services, self.initial_tickers)
        profit_service.profit_summary(self.exchange_services, self.end_tickers)

        dest_path = os.path.join(os.getcwd(), 'test.csv')
        profit_service.save_profit_history(dest_path)
        tdf = pandas.read_csv(dest_path)
        eq_(len(tdf), 2)
        for field in ProfitService.profit_summary_fields:
            assert_true(field in tdf.columns)
        os.remove(dest_path)