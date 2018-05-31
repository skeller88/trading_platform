"""
Computes pretax and post tax strategy profits relative to buy and hold (bh) BTC, both as alpha and absolute profits.

Unlike BacktestProfitService, does not need to maintain the state of exchange balances across two exchanges, because
the database does that. Also unlike BacktestProfitService, this service is not currently tracking capital gains taxes.
Ideally, it would, but as an initial effort, the service will subtract the strategy tax premium from profits.
"""
from collections import defaultdict
from decimal import Decimal

import pandas

from trading_platform.core.test.data import Defaults
from trading_platform.exchanges.data.financial_data import zero, one, one_hundred
from trading_platform.exchanges.data.pair import Pair


class ProfitService:
    """
    Relevant tax reading:
    - wash sale: https://www.investopedia.com/terms/t/tax_selling.asp
    """
    possible_bases = ['USDT', 'BTC', 'ETH']
    income_tax = Defaults.income_tax
    ltcg_tax = Defaults.ltcg_tax
    usdt_str = 'USDT'
    # fields contained in the response from self.profit_summary()
    profit_summary_fields = [
        'alpha',
        'net_profits_over_bh',

        'strat_return',
        'bh_return',

        'gross_profits',
        'bh_gross_profits',

        'taxes',
        'bh_taxes',

        'net_profits',
        'bh_net_profits',
   ]

    def __init__(self, **kwargs):
        self.balance_dao = kwargs.get('balance_dao')
        self.ticker_service = kwargs.get('ticker_service')
        self.start_balance_usd_value = kwargs.get('start_balance_usd_value')
        self.initial_tickers = kwargs.get('initial_tickers')
        self.balances = {}
        self.tickers = {}
        self.profit_history = []

    def fetch_balances_by_currency(self, exchange_services):
        # TODO - figure out how to make this class FinancialData instead of Decimal
        balances = defaultdict(Decimal)
        for exchange_service in exchange_services.values():
            balances_for_exchange = exchange_service.fetch_balances()
            for currency_name, balance in balances_for_exchange.items():
                balance = balances_for_exchange.get(currency_name)
                balance_value = balance.total if balance is not None else zero
                balances[currency_name] += balance_value

        self.balances = balances
        return self.balances

    def exchange_balances_usd_value(self, exchange_services, tickers_by_pair_name):
        balances = self.fetch_balances_by_currency(exchange_services)

        usd_value = zero

        for currency_name, amount in balances.items():
            usd_ticker = self.usd_value_for_currency(currency_name, tickers_by_pair_name)
            usd_value += amount * usd_ticker

        return usd_value

    def usd_value_for_currency(self, currency, tickers):
        if currency == self.usdt_str:
            return one

        for base in self.possible_bases:
            ticker = tickers.get(Pair.name_for_base_and_quote(quote=currency, base=base))
            if ticker:
                if base == self.usdt_str:
                    return ticker.bid
                else:
                    base_ticker_in_usd = tickers.get(Pair.name_for_base_and_quote(quote=base, base=self.usdt_str))
                    return ticker.bid * base_ticker_in_usd.bid

    def profit_summary(self, exchange_services, end_tickers):
        """
        Profit summary for strategy and buy and hold BTC.
        :param exchange_services:
        :param end_tickers: Assumes that tickers are pretty much the same across all exchanges.
        :return:
        """
        end_balance_usd_value = self.exchange_balances_usd_value(exchange_services, end_tickers)
        gross_profits = end_balance_usd_value - self.start_balance_usd_value
        taxes = max(gross_profits * (one - self.income_tax), zero)
        net_profits = gross_profits - taxes
        strat_return = net_profits / self.start_balance_usd_value * one_hundred

        btc_usdt_pair_name = Pair.name_for_base_and_quote(base='USDT', quote='BTC')
        inital_btc_ticker = self.initial_tickers.get(btc_usdt_pair_name)
        end_btc_ticker = end_tickers.get(btc_usdt_pair_name)
        bh_gross_profits = (end_btc_ticker.bid - inital_btc_ticker.bid) / inital_btc_ticker.bid * self.start_balance_usd_value
        bh_taxes = max(bh_gross_profits * (one - self.ltcg_tax), zero)
        bh_net_profits = bh_gross_profits - bh_taxes
        bh_return = bh_net_profits / self.start_balance_usd_value * one_hundred

        alpha = strat_return - bh_return
        net_profits_over_bh = net_profits - bh_net_profits
        profit_summary = {
            'alpha': alpha,
            'net_profits_over_bh': net_profits_over_bh,

            'strat_return': strat_return,
            'bh_return': bh_return,

            'gross_profits': gross_profits,
            'bh_gross_profits': bh_gross_profits,

            'taxes': taxes,
            'bh_taxes': bh_taxes,

            'net_profits': net_profits,
            'bh_net_profits': bh_net_profits,
        }
        self.profit_history.append(profit_summary)
        return profit_summary

    def save_profit_history(self, dest_path):
        """
        Convert list of dicts in self.profit_history to a pandas.DataFrame, and save to "dest_path".
        Args:
            dest_path:

        Returns:

        """

        snapshots_with_flattened_keys = list(map(self.flatten_snapshot, self.profit_history))
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