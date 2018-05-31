"""
Computes pretax and post tax strategy profits relative to buy and hold (bh) BTC, both as alpha and absolute profits.

Unlike BacktestProfitService, does not need to maintain the state of exchange balances across two exchanges, because
the database does that. Also unlike BacktestProfitService, this service is not currently tracking capital gains taxes.
Ideally, it would, but as an initial effort, the service will subtract the strategy tax premium from profits.
"""
from collections import defaultdict
from decimal import Decimal

from trading_platform.core.test.data import Defaults
from trading_platform.exchanges.data.financial_data import zero, one, one_hundred


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
        self.initial_btc_ticker = kwargs.get('initial_btc_ticker')
        self.balances = {}
        self.tickers = {}

    def fetch_balances_by_currency(self, exchange_services):
        # TODO - figure out how to make this class FinancialData instead of Decimal
        balances = defaultdict(Decimal)
        for exchange_service in exchange_services.values():
            balances_for_exchange = exchange_service.fetch_balances()
            for currency_name, balance in balances_for_exchange.items():
                balance = balances_for_exchange.get(currency_name)
                balance_value = balance.free if balance is not None else zero
                balances[currency_name] += balance_value

        self.balances = balances
        return self.balances

    def fetch_tickers_by_quote_and_base(self, exchange_services):
        tickers_list = self.ticker_service.fetch_latest_tickers(exchange_services)
        self.tickers = {}
        for ticker in tickers_list:
            self.tickers[(ticker.quote, ticker.base)] = ticker
        return self.tickers

    def exchange_balances_usd_value(self, exchange_services):
        balances = self.fetch_balances_by_currency(exchange_services)
        tickers = self.fetch_tickers_by_quote_and_base(exchange_services)

        usd_value = zero

        for currency_name, amount in balances.items():
            usd_ticker = self.usd_value_for_currency(currency_name, tickers)
            usd_value += amount * usd_ticker

        return usd_value

    def usd_value_for_currency(self, currency, tickers):
        if currency == self.usdt_str:
            return one

        for base in self.possible_bases:
            ticker = tickers.get((currency, base))
            if ticker:
                if base == self.usdt_str:
                    return ticker.bid
                else:
                    base_ticker_in_usd = tickers.get((base, self.usdt_str))
                    return ticker.bid * base_ticker_in_usd.bid

    def profit_summary(self, exchange_services, btc_ticker):
        end_balance_usd_value = self.exchange_balances_usd_value(exchange_services)
        gross_profits = end_balance_usd_value - self.start_balance_usd_value
        taxes = max(gross_profits * (one - self.income_tax), zero)
        net_profits = gross_profits - taxes
        strat_return = net_profits / self.start_balance_usd_value * one_hundred

        bh_gross_profits = (btc_ticker - self.initial_btc_ticker) / self.initial_btc_ticker * self.start_balance_usd_value
        bh_taxes = max(bh_gross_profits * (one - self.ltcg_tax), zero)
        bh_net_profits = bh_gross_profits - bh_taxes
        bh_return = bh_net_profits / self.start_balance_usd_value * one_hundred

        alpha = strat_return - bh_return
        net_profits_over_bh = net_profits - bh_net_profits

        return {
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
