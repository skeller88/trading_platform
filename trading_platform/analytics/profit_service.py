"""
Computes pretax and post tax strategy profits relative to buy and hold (bh) BTC, both as alpha and absolute profits.

Unlike BacktestProfitService, does not need to maintain the state of exchange balances across two exchanges, because
the database does that. Also unlike BacktestProfitService, this service is not currently tracking capital gains taxes.
Ideally, it would, but as an initial effort, the service will subtract the strategy tax premium from profits.
"""
import datetime
from collections import defaultdict
from decimal import Decimal
from functools import reduce
from typing import Dict, List

import pandas

from trading_platform.core.test.data import Defaults
from trading_platform.exchanges.data.balance import Balance
from trading_platform.exchanges.data.financial_data import zero, one, one_hundred, FinancialData
from trading_platform.exchanges.data.pair import Pair
from trading_platform.exchanges.data.ticker import Ticker
from trading_platform.exchanges.exchange_service_abc import ExchangeServiceAbc


class ProfitService:
    """
    Relevant tax reading:
    - wash sale: https://www.investopedia.com/terms/t/tax_selling.asp
    """
    possible_bases: List[str] = ['USDT', 'BTC', 'ETH']
    income_tax: FinancialData = Defaults.income_tax
    ltcg_tax: FinancialData = Defaults.ltcg_tax
    usdt_str: str = 'USDT'
    # fields contained in the response from self.profit_summary()
    profit_summary_fields: List[str] = [
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

    def __init__(self, exchanges_by_id: Dict[int, ExchangeServiceAbc], initial_datetime: datetime.datetime,
                 initial_tickers: Dict[str, Ticker]):
        # Will be defined on the first invocation of profit_summary().
        self.start_balance_usdt_value = None
        self.exchanges_by_id = exchanges_by_id
        self.initial_tickers = initial_tickers
        self.profit_history = []
        self.profit_summary(initial_datetime, self.initial_tickers)

    def fetch_balances_by_currency(self, exchange_services) -> Dict[str, FinancialData]:
        # TODO - figure out how to make this class FinancialData instead of Decimal
        balances = defaultdict(Decimal)
        for exchange_service in exchange_services.values():
            balances_for_exchange: Dict[str, Balance] = exchange_service.fetch_balances()
            for currency_name, balance in balances_for_exchange.items():
                balance: Balance = balances_for_exchange.get(currency_name)
                balances[currency_name] += balance.total

        return balances

    def exchange_balances_usdt_value(self, exchange_services, tickers_by_pair_name):
        balances: Dict[str, FinancialData] = self.fetch_balances_by_currency(exchange_services)

        usdt_value: FinancialData = zero
        for currency_name, balance in balances.items():
            usdt_value += balance * self.usdt_value_for_currency(currency_name, tickers_by_pair_name)

        return usdt_value

    def usdt_value_for_currency(self, currency, tickers):
        if currency == self.usdt_str:
            return one

        for base in self.possible_bases:
            ticker: Ticker = tickers.get(Pair.name_for_base_and_quote(quote=currency, base=base))
            if ticker:
                if base == self.usdt_str:
                    return ticker.bid
                else:
                    base_ticker_in_usd: Ticker = tickers.get(
                        Pair.name_for_base_and_quote(quote=base, base=self.usdt_str))
                    return ticker.bid * base_ticker_in_usd.bid

    def profit_summary(self, summary_datetime: datetime.datetime, end_tickers: Dict[str, Ticker]):
        """
        Profit summary for strategy vs. buy and hold BTC. This method is imprecise in that it doesn't calculate capital
        gains that would be incurred by liquidating the portfolio. But it taxes capital gains that have been calculated
        by the exchanges.
        :param exchange_services:
        :param end_tickers: Assumes that tickers are the same across all exchanges.
        :return:
        """
        end_balance_usdt_value: FinancialData = self.exchange_balances_usdt_value(self.exchanges_by_id, end_tickers)
        if self.start_balance_usdt_value is None:
            self.start_balance_usdt_value = end_balance_usdt_value

        gross_profits: FinancialData = end_balance_usdt_value - self.start_balance_usdt_value
        capital_gains: FinancialData = reduce(lambda sum, x: sum + x.capital_gains, self.exchanges_by_id.values(), zero)
        taxes: FinancialData = max(capital_gains * (one - self.income_tax), zero)
        net_profits: FinancialData = gross_profits - taxes
        strat_return: FinancialData = net_profits / self.start_balance_usdt_value

        btc_usdt_pair_name: str = Pair.name_for_base_and_quote(base='USDT', quote='BTC')
        inital_btc_ticker: Ticker = self.initial_tickers.get(btc_usdt_pair_name)
        end_btc_ticker: Ticker = end_tickers.get(btc_usdt_pair_name)
        bh_gross_profits: FinancialData = (
                                                      end_btc_ticker.bid - inital_btc_ticker.bid) / inital_btc_ticker.bid * self.start_balance_usdt_value
        bh_taxes: FinancialData = max(bh_gross_profits * (one - self.ltcg_tax), zero)
        bh_net_profits: FinancialData = bh_gross_profits - bh_taxes
        bh_return: FinancialData = bh_net_profits / self.start_balance_usdt_value

        alpha: FinancialData = strat_return - bh_return
        net_profits_over_bh: FinancialData = net_profits - bh_net_profits
        profit_summary: Dict = {
            'summary_datetime': summary_datetime,
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

        df: pandas.DataFrame = pandas.DataFrame(self.profit_history)
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
        flattened_snapshot: Dict = {}

        for key, val in profit_snapshot.items():
            if key == 'balances':
                for balance_key, balance_val in profit_snapshot[key].items():
                    flattened_snapshot[balance_key] = balance_val
            else:
                flattened_snapshot[key] = val

        return flattened_snapshot
