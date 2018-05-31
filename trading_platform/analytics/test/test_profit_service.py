import unittest

from nose.tools import assert_greater, assert_less

from trading_platform.analytics.profit_service import ProfitService
from trading_platform.exchanges.data.financial_data import FinancialData, zero, one_hundred, one
from trading_platform.exchanges.live import live_subclasses
from trading_platform.exchanges.live.live_subclasses import mvp_live
from trading_platform.exchanges.ticker_service import TickerService
from trading_platform.storage.daos.balance_dao import BalanceDao


class TestProfitService(unittest.TestCase):
    @classmethod
    def setUp(cls):
        cls.kwargs = {
            'balance_dao': BalanceDao(),
            'ticker_service': TickerService,
            'start_balance_usd_value': FinancialData(10000),
            'initial_btc_ticker': FinancialData(8000),
            'initial_eth_ticker': FinancialData(500)
        }
        cls.exchange_services = live_subclasses.instantiate(mvp_live())

    def test_balance_usd_value(self):
        ps = ProfitService(**self.kwargs)
        usd_value = ps.exchange_balances_usd_value(self.exchange_services)
        # Since tickers are always changing and exchange balances will change, the best we can do
        # is assert greater than zero, and verify manually that the total balance is what's expected.
        assert_greater(usd_value, zero)

    def test_profit_summary_end_balance_less_than_start_balance(self):
        """
        Assert that the profit summary has all of the expected fields, and that their values are approximately
        what would be expected.

        The following test assumes that the current usd value of all exchange balances is << start_balance_usd_value of
        5000, and that btc has significantly increased in value. in other words, high losses on the strategy
        strategy, and high gains on buy and hold. In this case, bh_taxes > taxes, bh_return >> strat_return,
        and gross_profits < 0.

        Returns:

        """
        self.kwargs['start_balance_usd_value'] = FinancialData(5000)
        ps = ProfitService(**self.kwargs)
        btc_ticker = self.kwargs['initial_btc_ticker'] * (one_hundred)
        profit_summary = ps.profit_summary(self.exchange_services, btc_ticker)
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

        The following test assumes that the current usd value of all exchange balances is >> start_balance_usd_value of
        50, and that btc has decreased in value. in other words, high gains on the strategy
        strategy, and high losses on buy and hold. In this case, taxes > bh_taxes, strat_return >> bh_return,
        and gross_profits > 0.

        Returns:

        """
        self.kwargs['start_balance_usd_value'] = FinancialData(50)
        ps = ProfitService(**self.kwargs)
        btc_ticker = self.kwargs['initial_btc_ticker'] * (one - FinancialData(.1))
        profit_summary = ps.profit_summary(self.exchange_services, btc_ticker)
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