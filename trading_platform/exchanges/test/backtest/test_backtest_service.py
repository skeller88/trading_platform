"""
nosetests test.services.exchange.backtest.test_backtest_service.TestBacktestService --nocapture
"""
import unittest
from copy import deepcopy

import datetime
import pandas
from nose.tools import eq_

from trading_platform.core.test.data import Defaults, eth_withdrawal_fee
from trading_platform.exchanges.src.backtest.backtest_service import BacktestService
from trading_platform.exchanges.src.data.enums import exchange_ids
from trading_platform.exchanges.src.data.financial_data import one, two, FinancialData, zero
from trading_platform.exchanges.src.data.pair import Pair
from trading_platform.utils.src.exceptions import InsufficientFundsException


class TestBacktestService(unittest.TestCase):
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

        self.te.set_buy_prices({
            self.pair.quote: self.initial_ticker
        })

        self.completion_timestamp = datetime.datetime.utcnow().timestamp()

    def test_balance(self):
        balances = self.te.fetch_balances()
        eq_(balances[self.pair.base], self.initial_base_capital)
        eq_(balances[self.pair.quote], self.initial_quote_capital)
        self.te.deposit_immediately(self.base, one)
        self.te.deposit_immediately(self.quote, one)
        eq_(balances[self.pair.base], self.initial_base_capital + one)
        eq_(balances[self.pair.quote], self.initial_quote_capital + one)

    def test_create_limit_buy_order(self):
        quote_amount_to_buy = one
        prev_wallet_quote = self.te.get_balance(self.quote)
        eq_(self.te.get_buy_price(self.quote), self.initial_ticker)
        new_price = self.initial_ticker * FinancialData(.5)
        self.te.create_limit_buy_order(pair=self.pair, amount=quote_amount_to_buy, price=new_price)
        eq_(self.te.get_buy_price(self.quote), new_price)
        eq_(self.te.get_balance(self.quote), prev_wallet_quote + quote_amount_to_buy)
        eq_(self.te.get_balance(self.base),
            self.initial_base_capital - quote_amount_to_buy * new_price * (one + self.te.trade_fee))

    def test_buy_min_base_order_value(self):
        quote_amount_to_buy = one
        prev_wallet_quote = self.te.get_balance(self.quote)
        eq_(self.te.get_buy_price(self.quote), self.initial_ticker)
        new_price = self.initial_ticker * FinancialData(.5)
        self.te.min_base_order_value = quote_amount_to_buy * new_price
        quote_purchased = self.te.create_limit_buy_order(pair=self.pair, amount=quote_amount_to_buy, price=new_price)
        eq_(quote_purchased.amount, quote_amount_to_buy)
        eq_(self.te.get_balance(self.quote), prev_wallet_quote + quote_amount_to_buy)
        eq_(self.te.get_balance(self.base),
            self.initial_base_capital - quote_amount_to_buy * new_price * (one + self.te.trade_fee))

    def test_buy_below_min_base_order_value(self):
        quote_amount_to_buy = one
        prev_wallet_quote = self.te.get_balance(self.quote)
        eq_(self.te.get_buy_price(self.quote), self.initial_ticker)
        new_price = self.initial_ticker * FinancialData(.5)
        self.te.min_base_order_value = quote_amount_to_buy * new_price + 1
        quote_purchased = self.te.create_limit_buy_order(pair=self.pair, amount=quote_amount_to_buy, price=new_price)
        eq_(quote_purchased.amount, zero)
        eq_(self.te.get_balance(self.quote), prev_wallet_quote)
        eq_(self.te.get_balance(self.base), self.initial_base_capital)

    def test_buy_all(self):
        prev_wallet_quote = self.te.get_balance(self.quote)
        quote_purchased = self.te.buy_all(self.pair, self.price)
        assert (self.te.get_balance(self.base) == 0)
        assert (quote_purchased.amount > 0)
        assert (self.te.get_balance(self.quote) > prev_wallet_quote)

    def test_create_limit_buy_order_insufficient_funds(self):
        try:
            self.te.create_limit_buy_order(pair=self.pair, amount=self.te.get_balance(self.quote) + one,
                                           price=self.price)
            raise Exception("Should have thrown an exception")
        except InsufficientFundsException:
            pass

    def test_sell_no_capital_gains_or_losses(self):
        prev_wallet_base = self.te.get_balance(self.base)
        prev_wallet_quote = self.te.get_balance(self.quote)
        # divide so that we can confirm division doesn't cause any rounding errors
        quote_to_sell = self.te.get_balance(self.quote) / two

        base_received = self.te.create_limit_sell_order(self.pair, quote_to_sell, self.price, None)
        assert (self.te.get_balance(self.base) == prev_wallet_base + base_received)
        assert (self.te.get_balance(self.quote) == prev_wallet_quote - quote_to_sell)
        assert (self.te.capital_gains == 0)
        assert (self.te.capital_losses == 0)

    def test_sell_capital_gains(self):
        prev_wallet_base = self.te.get_balance(self.base)
        prev_wallet_quote = self.te.get_balance(self.quote)
        quote_to_sell = self.te.get_balance(self.quote) / two
        buy_price = self.te.get_buy_price(self.quote)
        sell_price = buy_price * (one + FinancialData(.01))

        base_received = self.te.create_limit_sell_order(self.pair, quote_to_sell, sell_price, None)
        assert (self.te.get_balance(self.base) == prev_wallet_base + base_received)
        assert (self.te.get_balance(self.quote) == prev_wallet_quote - quote_to_sell)
        assert (self.te.capital_gains == quote_to_sell * (sell_price - buy_price))
        assert (self.te.capital_gains > 0)
        assert (self.te.capital_losses == 0)

    def test_sell_capital_losses(self):
        prev_wallet_base = self.te.get_balance(self.base)
        prev_wallet_quote = self.te.get_balance(self.quote)
        quote_to_sell = self.te.get_balance(self.quote) / two
        buy_price = self.te.get_buy_price(self.quote)
        sell_price = buy_price * (one - FinancialData(.01))

        base_received = self.te.create_limit_sell_order(self.pair, quote_to_sell, sell_price, None)
        assert (self.te.get_balance(self.base) == prev_wallet_base + base_received)
        assert (self.te.get_balance(self.quote) == prev_wallet_quote - quote_to_sell)
        assert (self.te.capital_gains == 0)
        assert (self.te.capital_losses == quote_to_sell * abs(sell_price - buy_price))
        assert (self.te.capital_losses > 0)

    def test_sell_min_base_order_value(self):
        prev_wallet_base = self.te.get_balance(self.base)
        prev_wallet_quote = self.te.get_balance(self.quote)
        quote_to_sell = self.te.get_balance(self.quote) / two
        buy_price = self.te.get_buy_price(self.quote)
        sell_price = buy_price * (one - FinancialData(.01))
        self.te.min_base_order_value = quote_to_sell * sell_price

        base_received = self.te.create_limit_sell_order(self.pair, quote_to_sell, sell_price, None)
        assert (self.te.get_balance(self.base) == prev_wallet_base + base_received)
        assert (self.te.get_balance(self.quote) == prev_wallet_quote - quote_to_sell)
        assert (self.te.capital_gains == 0)
        assert (self.te.capital_losses == quote_to_sell * abs(sell_price - buy_price))
        assert (self.te.capital_losses > 0)

    def test_sell_below_min_base_order_value(self):
        prev_wallet_base = self.te.get_balance(self.base)
        prev_wallet_quote = self.te.get_balance(self.quote)
        quote_to_sell = self.te.get_balance(self.quote) / two
        buy_price = self.te.get_buy_price(self.quote)
        sell_price = buy_price * (one - FinancialData(.01))
        self.te.min_base_order_value = quote_to_sell + 1 * sell_price

        base_received = self.te.create_limit_sell_order(self.pair, quote_to_sell, sell_price, None)
        eq_(base_received, zero)
        assert (self.te.get_balance(self.base) == prev_wallet_base)
        assert (self.te.get_balance(self.quote) == prev_wallet_quote)

    def test_sell_all(self):
        prev_wallet_quote = self.te.get_balance(self.quote)
        prev_wallet_base = self.te.get_balance(self.base)
        actual_base_received = self.te.sell_all(self.pair, self.price)
        expected_base_received = self.price * prev_wallet_quote / (one + self.te.trade_fee)

        assert (actual_base_received == expected_base_received)
        assert (self.te.get_balance(self.quote) == zero)
        assert (self.te.capital_gains == zero)
        assert (self.te.capital_losses == zero)
        assert (self.te.get_balance(self.base) == prev_wallet_base + expected_base_received)

    def test_withdraw(self):
        """
        Withdraw currency from an exchange and deposit into another exchange.
        Returns:

        """
        dest_exchange = deepcopy(self.te)
        prev_balance = self.te.get_balance(self.base)
        expected_base_withdrawn = self.te.get_balance(self.base) - self.te.withdrawal_fee_for_currency(self.base)
        actual_base_withdrawn = self.te.withdraw(self.base, self.te.get_balance(self.base), dest_exchange,
                                                 params={'completion_timestamp': self.completion_timestamp})
        dest_exchange.update_pending_deposits(self.completion_timestamp)
        assert (self.te.get_balance(self.base) == zero)
        assert (dest_exchange.get_balance(self.base) == prev_balance + actual_base_withdrawn)
        assert (expected_base_withdrawn == actual_base_withdrawn)

    def test_withdraw_no_rounding_errors(self):
        dest_exchange = deepcopy(self.te)
        prev_balance = self.te.get_balance(self.base)
        base_to_spend_on_withdrawal = self.te.get_balance(self.base) / two
        expected_base_withdrawn = base_to_spend_on_withdrawal - self.te.withdrawal_fee_for_currency(self.base)
        actual_base_withdrawn = self.te.withdraw(self.base, base_to_spend_on_withdrawal, dest_exchange,
                                                 params={'completion_timestamp': self.completion_timestamp})
        dest_exchange.update_pending_deposits(self.completion_timestamp)
        assert (self.te.get_balance(self.base) == prev_balance - base_to_spend_on_withdrawal)
        assert (dest_exchange.get_balance(self.base) == prev_balance + actual_base_withdrawn)
        assert (expected_base_withdrawn == actual_base_withdrawn)

    def test_withdraw_all(self):
        dest_exchange = deepcopy(self.te)
        prev_balance = self.te.get_balance(self.base)
        base_withdrawn = self.te.withdraw_all(self.base, dest_exchange,
                                              params={'completion_timestamp': self.completion_timestamp})
        dest_exchange.update_pending_deposits(self.completion_timestamp)
        eq_(self.te.get_balance(self.base), zero)
        eq_(dest_exchange.get_balance(self.base), prev_balance + base_withdrawn)
        eq_(base_withdrawn, self.initial_base_capital - self.te.withdrawal_fee_for_currency(self.base))

        prev_balance = self.te.get_balance(self.quote)
        quote_withdrawn = self.te.withdraw_all(self.quote, dest_exchange,
                                               params={'completion_timestamp': self.completion_timestamp})
        dest_exchange.update_pending_deposits(self.completion_timestamp)
        eq_(self.te.get_balance(self.quote), zero)
        eq_(dest_exchange.get_balance(self.quote), prev_balance + quote_withdrawn)
        eq_(quote_withdrawn, self.initial_quote_capital - self.te.withdrawal_fee_for_currency(self.quote))
