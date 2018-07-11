"""
Computes strategy profits relative to buy and hold (bh), either alpha or absolute profits. Maintains the state of
exchange balances across two exchanges, the high and the low exchange.
"""
import pandas

from trading_platform.exchanges.backtest.backtest_exchange_service import BacktestExchangeService
from trading_platform.exchanges.data.financial_data import FinancialData, zero, one_hundred


class BacktestProfitService:
    """
    Relevant tax reading:
    - wash sale: https://www.investopedia.com/terms/t/tax_selling.asp
    """
    # columns contained in a snapshot, apart from balance data
    columns = [
        'alpha',
        'strat_return',
        'bh_return',
        'profits',
        'bh_profits',
        'profits_over_bh'
   ]

    def __init__(self, income_tax, ltcg_tax, he, le, initial_tickers):
        self.income_tax = FinancialData(income_tax)
        self.ltcg_tax = FinancialData(ltcg_tax)
        self.he = he
        self.le = le
        # A str representing the base currency.
        # Assume he and le have the same base. The base is used to calculate net profits in USD.
        # assume that initially, the tickers on he and le are ==.
        self.initial_tickers = initial_tickers
        self.profit_snapshots = []
        self.idx = 0

    def profit_summary(self, end_tickers):
        """
        Args:
            end_tickers:
            after_tax:
            end_tickers: Dict(currency name, currency ticker in base). All tickers should have the same base.

        Returns:
        """
        snapshot = {}
        snapshot['balances'] = self.balances_across_exchanges()

        # The first snapshot determines the balance of buy and hold. So alpha and net profits will be zero.
        if len(self.profit_snapshots) == 0:
            snapshot['alpha'] = zero
            snapshot['profits'] = zero
            snapshot['strat_return'] = zero
            snapshot['bh_return'] = zero
            snapshot['profits'] = zero
            snapshot['bh_profits'] = zero
            snapshot['profits_over_bh'] = zero
        else:
            strat_return, bh_return = self.rates_of_return(end_tickers)
            snapshot['strat_return'] = strat_return
            snapshot['bh_return'] = bh_return
            snapshot['alpha'] = strat_return - bh_return

            start_balance = self.profit_snapshots[0]['balances']
            profits, bh_profits = self.net_profits(start_balance, end_tickers)
            snapshot['profits'] = profits
            snapshot['bh_profits'] = bh_profits
            snapshot['profits_over_bh'] = profits - bh_profits
        self.profit_snapshots.append(snapshot)
        return snapshot

    def balances_across_exchanges(self):
        return BacktestProfitService.merge_and_sum_dicts(self.he.fetch_balances(), self.le.fetch_balances())

    def strat_profit_over_bh(self, end_tickers):
        start_balance = self.profit_snapshots[0]['balances']
        profits, bh_profits = self.net_profits(start_balance, end_tickers)
        return profits - bh_profits

    def net_profits(self, start_balance, end_tickers):
        """
        Args:
            start_balance:
            end_tickers pandas.DataFrame: assumes there is a USDT ticker for each currency.

        Returns:

        """
        start_balance_value = BacktestExchangeService.total_usdt_value(start_balance, self.initial_tickers)

        # I'm not the biggest fan of this line. Ideally it would be self.profit_history[len(self.profit_history) - 1],
        # but he.capital_gains and le.capital_gains reflect the current state of the exchange. And the last element
        # in self.profit_history may not match that. So this approach seemed like the lesser of two evils. Make sure to call .alpha() right after
        # .create_balance_snapshot(), or visa versa. Otherwise the alpha may not match the balance snapshot.
        end_balance = self.balances_across_exchanges()
        end_balance_value = BacktestExchangeService.total_usdt_value(end_balance, end_tickers)
        gross_profits = end_balance_value - start_balance_value
        # Due to the wash sale rule, can't deduct capital losses. We could refine the strategy to sell everything at the
        # end of the year and realize capital losses, but that's not implemented for now. Let's see if strategy is profitable
        # without that strategy.
        capital_gains = BacktestProfitService.merge_and_sum_dicts(self.he.capital_gains, self.le.capital_gains)
        taxes = max(BacktestExchangeService.total_usdt_value(capital_gains, end_tickers), 0) * self.income_tax
        net_profits = gross_profits - taxes

        end_bh_balance_value = BacktestExchangeService.total_usdt_value(start_balance, end_tickers)
        # unlike when calculating arg_gross_profits, compute unrealized profits if the balances were to be liquidated
        bh_gross_profits = end_bh_balance_value - start_balance_value
        bh_taxes = max(bh_gross_profits, 0) * self.ltcg_tax
        bh_net_profits = bh_gross_profits - bh_taxes

        return net_profits, bh_net_profits

    def rates_of_return(self, end_tickers):
        start_balance = self.profit_snapshots[0]['balances']
        profits, bh_profits = self.net_profits(start_balance, end_tickers)
        start_balance_usdt_value = BacktestExchangeService.total_usdt_value(start_balance, self.initial_tickers)
        strat_return = profits / start_balance_usdt_value * one_hundred
        bh_return = bh_profits / start_balance_usdt_value * one_hundred
        return strat_return, bh_return

    def alpha(self, end_tickers):
        strat_return, bh_return = self.rates_of_return(end_tickers)
        return strat_return - bh_return

    def save_profit_history(self, dest_path):
        """
        Convert list of dicts in self.profit_history to a pandas.DataFrame, and save to "dest_path".
        Args:
            dest_path:

        Returns:

        """

        snapshots_with_flattened_keys = list(map(self.flatten_snapshot, self.profit_snapshots))
        df = pandas.DataFrame(snapshots_with_flattened_keys)
        df.to_csv(dest_path, index=False)

    @staticmethod
    def flatten_snapshot(profit_snapshot):
        """
        Flatten nested dictionary of balance state. The balance state needs to be a separate key because methods
        such as net_profits use the balances alone to calculate alpha and profits. In other words, the
        balance keys can't be flattened and at the same level as the alpha and profits keys.
        Yes:
        {'balances': {'ETH': 2}, 'alpha': 3}

        No:
        {'ETH': 2, 'alpha': 3}

        Args:
            profit_snapshot:

        Returns:

        """
        flattened_snapshot = {}

        for key, val in profit_snapshot.items():
            if key == 'balances':
                for balance_key, balance_val in profit_snapshot[key].items():
                    flattened_snapshot[balance_key] = balance_val
            else:
                flattened_snapshot[key] = val

        return flattened_snapshot


    @staticmethod
    def merge_and_sum_dicts(x, y):
        """
        Merge common elements, add unique elements
        https://stackoverflow.com/questions/10461531/merge-and-sum-of-two-dictionaries
        Args:
            x:
            y:

        Returns dict: merged dicts
        """
        return {k: x.get(k, zero) + y.get(k, zero) for k in set(x) | set(y)}