"""
Exchange services that are composed of a BacktestService instance are used in backtests.

This class uses in-memory data structures to maintain exchange balance and order state, while stub exchange operations
such as buying, selling, and fetching balances. That way, the live exchange can be mocked.
The class fetches historical ticker data from csv files and exposes that data as a stream to enable scalable backtesting.

The class supports managing state of balances for multiple currencies, but only keeps track of capital gains and losses
with respect to a single base currency. This seems fine for now because historical data is split up by exchange and pair.
So backtests could be run on different base currencies simultaneously.

The class is used in other ExchangeServiceAbc classes via the composition/delegation/proxy pattern. There's a lot of different names for
this pattern, but the idea is that any class that is composed of an instance of the BacktestService class will delegate certain
methods to that class. There's debate about whether multiple composition is better than multiple inheritance. My initial
opinion is that multiple composition is more flexible and a bit easier to reason about:
See an example here http://python-3-patterns-idioms-test.readthedocs.io/en/latest/Fronting.html
"""
import datetime
from collections import defaultdict
from functools import reduce
from heapq import heappush, heappop

from decimal import Decimal

from trading_platform.exchanges.data.deposit_destination import DepositDestination
from trading_platform.exchanges.data.enums import exchange_ids
from trading_platform.exchanges.data.enums.order_side import OrderSide
from trading_platform.exchanges.data.enums.order_status import OrderStatus
from trading_platform.exchanges.data.enums.order_type import OrderType
from trading_platform.exchanges.data.financial_data import FinancialData, zero, one
from trading_platform.exchanges.data.order import Order
from trading_platform.exchanges.data.pair import Pair
from trading_platform.exchanges.exchange_service_abc import ExchangeServiceAbc
from trading_platform.utils.datetime_operations import utc_timestamp
from trading_platform.utils.exceptions import InsufficientFundsException
from trading_platform.utils.logging import print_if_debug_enabled

insufficient_funds = "Insufficient Funds"


class BacktestService(ExchangeServiceAbc):
    def __init__(self, exchange_id, trade_fee, withdrawal_fees, echo):
        """
        Args:
            exchange_id:
            trade_fee FinancialData: percent trade fee. Adds to base amount spent on buy orders and subtracts from quote amount received on sell orders.
            withdrawal_fees:
            base: base currency for all sales. Ensure that capital gains are consistently calculated.
            echo: If True, print output of "print_if_echo_enabled" invocations. Otherwise, swallow.
            min_base_order_value FinancialData: minimum base value of the order in order for an order to be placed.
                Otherwise, the instance determines that it's not worth it to place the order.
        """
        super().__init__(key=None, secret=None, trade_fee=trade_fee)
        # Used by print statements and for writing balance data to the proper filename
        self.exchange_id = exchange_id
        self.exchange_name = exchange_ids.to_name(exchange_id)

        # Exchange-specific configuration
        self.trade_fee = trade_fee
        # pd.DataFrame with index of "currency" names, and "withdrawal_fee" column containing withdrawal fee for that
        # currency.
        self.__withdrawal_fees = withdrawal_fees

        # Store the state of balances
        self.__balances = defaultdict(Decimal)

        # Stores the last buy price of a given currency. Used for calculating capital gains and losses.
        # updated for a given quote currency when buying the currency or depositing currency bought on another exchange
        # Note that only one buy price can be tracked at a time for a given currency.
        self.__buy_prices = {}

        # Updated as trades occur. Used to calculate taxes per base currency.
        self.capital_gains = defaultdict(Decimal)
        # Updated as trades occur. Used to calculate taxes per base currency.
        self.capital_losses = defaultdict(Decimal)
        self.balance_history = []

        # In order to simulate transfer time of currencies, between exchanges, store pending deposits to the wallet
        # in a priority queue sorted by the timestamp at which the deposit will be available, and update the balance
        # with the deposit once the timestamp has been reached.
        self.__pending_deposits = []
        self.__tickers = {}

        self.echo = echo

    ###########################################
    # Trading - Orders
    ###########################################

    def cancel_order(self, order_id, pair, params={}):
        raise NotImplementedError('cancel_order')

    def create_limit_buy_order(self, pair, amount, price, *params):
        """

        Args:
            pair: unused in this ExchangeServiceAbc implementation
            amount: quote to purchase after fees
            price: amount to spend
            *params:

        Returns FinancialData: amount of quote purchased after fees

        """
        base = pair.base
        quote = pair.quote
        amount = FinancialData(amount)
        base_plus_fees = self.base_needed_to_buy_currency_after_trade_fees(amount=amount, price=price)
        if base_plus_fees == zero:
            return zero
        if self.below_min_base_order_value(base_plus_fees, one):
            return zero
        # deal with small rounding errors
        if (self.__balances[base] - base_plus_fees) / abs(base_plus_fees) >= -1e-6:
            print_if_debug_enabled(self.echo, "\n%s\tBuying\t%f@%f, base_needed_to_buy_quote_amount:%f" % (
            self.name, amount, price, base_plus_fees))
            self.print_balances()
            self.__balances[base] -= base_plus_fees
            # deal with small rounding errors
            self.__balances[base] = max(self.__balances[base], zero)
            self.__balances[quote] += amount
            self.print_balances()
            self.__buy_prices[pair.name] = price

            return Order(**{
                # exchange-related data
                'exchange_id': self.exchange_id,
                'order_type': OrderType.limit,
                'order_id': str(utc_timestamp()),

                # numerical data
                'amount': amount,
                'price': price,

                # metadata
                'base': pair.base,
                'quote': pair.quote,
                'order_status': OrderStatus.filled,
                'order_side': OrderSide.buy
            })
        else:
            raise InsufficientFundsException('{0} base needed to buy {1} of quote, only {2} base available'.format(
                base_plus_fees, amount, self.__balances[base]))

    def create_limit_sell_order(self, pair, amount, price, *params):
        """
        Specify how much quote you want to sell, and the trading fee is subtracted from the quote sold. Different from
        .buy() in that the fees are not added to the amount to sell. The fees are subtracted. This is how the exchanges
        work.
        return: base_amount_received after fees. Will always be < amount * self.ticker.
        # Assume that the same base currency is used for every sell order.
        Args:
            pair:
            amount:
            price FinancialData: in base currency
            *params:

        Returns FinancialData: base received after fees

        """
        amount = FinancialData(amount)
        if amount <= zero:
            return zero
        if self.below_min_base_order_value(amount, price):
            return zero
        if self.__balances[pair.quote] >= amount:
            # print(self.name + "\tSelling\t%f@%f" % (amount, self.ticker))
            base_amount_received = price * amount / (one + self.trade_fee)
            self.__balances[pair.base] += base_amount_received
            self.__balances[pair.quote] -= amount

            gross = (price - self.__buy_prices[pair.name]) * FinancialData(amount)

            if gross >= 0:
                self.capital_gains[pair.base] += gross
            else:
                self.capital_losses[pair.base] += abs(gross)

            return Order(**{
                # exchange-related data
                'exchange_id': self.exchange_id,
                'order_type': OrderType.limit,
                'order_id': str(utc_timestamp()),

                # numerical data
                'amount': amount,
                'price': price,

                # metadata
                'base': pair.base,
                'quote': pair.quote,
                # The exchange won't return the order status when the order is placed, so assume it's open
                'order_status': OrderStatus.filled,
                'order_side': OrderSide.sell
            })

        else:
            # print('Could not sell', insufficient_funds)
            raise InsufficientFundsException('{0} quote needed to sell, only {1} quote available'.format(
                amount, self.__balances[pair.quote]))

    def fetch_closed_orders(self):
        return {}

    def fetch_open_orders(self, symbol=None):
        return {}

    def buy_all(self, pair, price):
        amount = FinancialData(self.__balances[pair.base] / (price * (one + self.trade_fee)))
        return self.create_limit_buy_order(pair=pair, amount=amount, price=price)

    def sell_all(self, pair, price):
        return self.create_limit_sell_order(pair, self.__balances[pair.quote], price)

    ###########################################
    # Account state
    ###########################################
    def get_balance(self, currency):
        return self.__balances[currency]

    def fetch_balances(self):
        return self.__balances

    def set_buy_prices(self, buy_prices):
        self.__buy_prices = buy_prices

    def get_buy_price(self, currency):
        return self.__buy_prices.get(currency)

    @staticmethod
    def total_usdt_value(funds, tickers_by_currency):
        """
        Value of all funds in USDT currency. First, calculates the value of all tickers in BTC or
        ETH. Then, converts to USDT.

        This method is static because for backtesting, the value of the exchange balance at various points in time
        needs to be calculated.

        Args:
            funds: can be either capital gains or balances
            tickers_by_currency: assumed to have the same base

        Returns FinancialData:

        """
        def usdt_value(total_usdt_value, currency):
            usdt_pair = Pair(base='USDT', quote=currency)
            currency_usdt_price = tickers_by_currency.get(usdt_pair.name)

            if currency_usdt_price is None:
                for base in ['BTC', 'ETH']:
                    pair = Pair(base=base, quote=currency)
                    currency_base_price = tickers_by_currency.get(pair.name)
                    if currency_base_price is not None:
                        usdt_pair = Pair(base='USDT', quote=base)
                        base_usdt_price = tickers_by_currency.get(usdt_pair.name)
                        currency_usdt_price = currency_base_price * base_usdt_price
                        break

            return total_usdt_value + funds.get(currency, zero) * currency_usdt_price

        return FinancialData(reduce(usdt_value, funds, zero))

    def base_needed_to_buy_currency_after_trade_fees(self, amount, price):
        """
        Used to determine how much currency to buy and sell on each exchange in a way that increase the amount of base
        and quote
        Args:
            amount:
            price:

        Returns:

        """
        amount = FinancialData(amount)
        if amount <= zero:
            return zero
        base_amount = amount * FinancialData(price)
        return FinancialData(base_amount * (one + self.trade_fee))

    def print_balances(self):
        print_if_debug_enabled(self.echo, self.__balances)

    def convert_currency_withdrawal_fee(self, currency_to_convert, price_of_target_currency):
        """
        Convert one currency withdrawal to its value in another currency.

        For example, Say POWR ticker is .05.
        .008 ETH withdrawal fee * (POWR / .05 ETH) = .16 POWR

        Args:
            currency_to_convert:
            price_of_target_currency: price of target currency in currency_to_convert. For example, if converting BTC
                to ETH, this would be the price of 1 ETH, in BTC.

        Returns:

        """
        return self.withdrawal_fee_for_currency(currency_to_convert) / price_of_target_currency

    def currency_sale_value_post_fees(self, quote, base, quote_price):
        """
        Value, in quote, of the base that would be gained from selling all of the quote, after trading and
        base withdrawal fees. The reason for this method is to calculate which exchange has the limiting amount of
        funds for an arbitrage. The exchange funds need to be standardized to the same quote and exchange-specific
        fees need to be applied. The key to this method is that it subtracts base withdrawal fees, not quote withdrawal
        fees.

        I can't think of a more concise method name. Open to suggestions.
        Args:
            quote_price:

        Returns FinancialData: base sale value post fees, in the quote
        """
        base_withdrawal_fee_in_quote = self.convert_currency_withdrawal_fee(base, quote_price)
        # the "quote_price" variable cancels out mathematically
        return self.__balances[quote] / (one + self.trade_fee) - base_withdrawal_fee_in_quote

    def currency_purchased_value_post_fees(self, currency, currency_price, base_amount):
        """
        How much currency the exchange could buy and withdraw after trade and withdrawal fees
        Args:
            base_amount:
            currency_price: price of currency
            base:
            currency:
        """
        return base_amount / (currency_price * (one + self.trade_fee)) - self.withdrawal_fee_for_currency(currency)

    def withdrawal_fee_for_currency(self, currency):
        # hack for now
        if currency == 'BCH':
            currency = 'BCC'

        # values in dataframe are in float type, which is not compatible with the FinancialData type (Decimal)
        return FinancialData(self.__withdrawal_fees.at[currency.upper(), 'withdrawal_fee'])

    def below_min_base_order_value(self, currency_amount, currency_price):
        # TODO - compute for different bases
        # return currency_amount * currency_price < self.min_base_order_value
        return False

    ###########################################
    # Market state
    ###########################################

    def fetch_market_symbols(self):
        raise NotImplementedError('fetch_market_symbols')

    def fetch_latest_tickers(self):
        return

    def set_tickers(self, tickers):
        self.__tickers = tickers

    def get_ticker(self, pair_name):
        return self.__tickers.get(pair_name)

    ###########################################
    # Trading - Funding
    ###########################################
    def deposit_immediately(self, currency, amount):
        """
        Deposit funds and immediately check pending deposits. Set the current timestamp to equal the deposit completion
        timestamp to trigger the deposit. The completion and current timestamps are both set to 0 so that this method
        doesn't cause other deposits to be triggered unexpectedly. No timestamp is going to be <= 0 except 0.
        Args:
            currency:
            amount:
        Returns:
        """
        completion_timestamp = 0
        self.deposit(currency, amount, completion_timestamp)
        self.update_pending_deposits(completion_timestamp)

    def deposit(self, currency, amount, completion_timestamp):
        """
        Deposit currency into exchange.
        Used in testing. In production, accounts are funded by withdrawing from seed accounts that have been funded
        manually, such as GDAX.
        Args:
            currency:
            amount:
            completion_timestamp int: timestamp, in seconds, when the deposit will be completed
        Returns:
        """
        heappush(self.__pending_deposits, (completion_timestamp, currency, amount))

    def fetch_pending_deposits(self):
        """
        Returns dict(str, FinancialData): containing the amount of each currency
        """
        deposits_dict = defaultdict(int)
        for deposit in self.__pending_deposits:
            deposits_dict[deposit[1]] += deposit[2]

        return deposits_dict

    def update_pending_deposits(self, current_timestamp):
        """
        Deposit any pending deposits that have a completion_timestamp < current_timestamp. The heap will maintain the
        ordering of the deposits.

        TODO - add tests

        Args:
            current_timestamp float:
        Returns:
        """
        while len(self.__pending_deposits) > 0 and self.__pending_deposits[0][0] <= current_timestamp:
            pending_deposit_completion_timestamp = self.__pending_deposits[0][0]
            pd_dt = datetime.datetime.fromtimestamp(pending_deposit_completion_timestamp)
            c_dt = datetime.datetime.fromtimestamp(current_timestamp)
            deposit = heappop(self.__pending_deposits)
            self.__balances[deposit[1]] += deposit[2]

    def fetch_deposit_destination(self, currency, params):
        """
        https://github.com/ccxt/ccxt/wiki/Manual#deposit
        Args:
            currency:
            params:

        Returns:

        """
        return DepositDestination(address=self, tag=None, status=DepositDestination.ok_status)

    def withdraw(self, currency, amount, dest_exchange, tag=None, params={}):
        """
        Args:
            currency:
            amount (FinancialData): amount of currency to withdraw. Withdrawal fees are subtracted from amount, so the actual amount
                withdrawn will be less.
            dest_exchange: reference to an exchange composed of BacktestService. The dictionary has to be passed by reference
                in order for the balance to be properly updated. It's not the best naming because ideally this parameter
                would be named "balances", not "address_or_dest_exchange". but the interface needs to be compatible with that of a live
                exchange.
            tag:
            params: "completion_timestamp": float, timestamp that determines when the deposit on the dest_exchange
                will be settled

        Returns:

        """
        if self.__balances[currency] >= amount:
            # print(self.name + "\tWithdrawing\t%f quote" % amount)
            self.__balances[currency] -= amount
            amount_withdrawn = amount - self.withdrawal_fee_for_currency(currency)
            dest_exchange.deposit(currency, amount_withdrawn, params.get('completion_timestamp'))
            return amount_withdrawn
        else:
            raise InsufficientFundsException('{0} needed to withdraw, only {1} available'.format(
                amount, self.__balances[currency]))

    def withdraw_all(self, currency, address, tag=None, params={}):
        return self.withdraw(currency, self.__balances[currency], address, params=params)

    @staticmethod
    def standardize_limit_order_response(order_response):
        pass

    @staticmethod
    def id():
        return None

    @staticmethod
    def name():
        return None
