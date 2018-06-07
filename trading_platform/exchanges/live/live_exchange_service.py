from typing import Dict

import ccxt
from ccxt import ExchangeError

from trading_platform.core.constants import exchange_pairs
from trading_platform.exchanges.data import standardizers
from trading_platform.exchanges.data.balance import Balance
from trading_platform.exchanges.data.deposit_destination import DepositDestination
from trading_platform.exchanges.data.enums import exchange_ids
from trading_platform.exchanges.data.enums.order_side import OrderSide
from trading_platform.exchanges.data.enums.order_status import OrderStatus
from trading_platform.exchanges.data.financial_data import FinancialData, zero, one
from trading_platform.exchanges.data.order import Order
from trading_platform.exchanges.data.ticker import Ticker
from trading_platform.exchanges.exchange_service_abc import ExchangeServiceAbc
from trading_platform.utils import api_request_msgs
from trading_platform.utils.api_request_msgs import LIMIT_BUY_ORDER_ATTEMPT, LIMIT_SELL_ORDER_ATTEMPT, LIMIT_BUY_ORDER_ERR, \
    LIMIT_SELL_ORDER_ERR
from trading_platform.utils.datetime_operations import utc_timestamp
from trading_platform.utils.http_utils import make_api_limit_order_request, make_api_request


class LiveExchangeService(ExchangeServiceAbc):
    """
    Bridge class for any client library we use. Don't call an exchange client library directly, instead call via this
    wrapper abstract class method.
    """

    def __init__(self, exchange_name, exchange_id, client, key, secret, trade_fee, withdrawal_fees):
        """
        Args:
            key str:
            secret str:
            withdrawal_fees pandas.DataFrame:
        """
        super().__init__(key=key, secret=secret, trade_fee=trade_fee)
        self.exchange_id = exchange_id
        self.exchange_name = exchange_name
        self.__client = client
        self.__balances = {}
        self.__open_orders = {}
        self.__tickers = {}
        self.__withdrawal_fees = withdrawal_fees

    ###########################################
    # Trading - Orders
    ###########################################

    def cancel_order(self, order_id, pair):
        """
        :param order_id: str
        :param pair: Pair
        :return:
        """
        self.__client.verbose = True
        if self.exchange_id == exchange_ids.binance:
            order_id = int(order_id)
        response = make_api_request(api_request_msgs.CANCEL_ORDER_ERR.format(self.exchange_name),
                                    self.__client.cancel_order, order_id, pair.name_for_exchange_clients, {})
        self.__client.verbose = False
        if response:
            return Order(**{
                'exchange_id': self.exchange_id,
                'order_id': order_id,
                'order_status': OrderStatus.cancelled,
                'base': pair.base,
                'quote': pair.quote
            })

        raise Exception('Order was not cancelled', response)

    def create_limit_buy_order(self, pair, amount, price, *params):
        return self.create_limit_order(OrderSide.buy, pair, amount, price, *params)

    def create_limit_sell_order(self, pair, amount, price, *params):
        return self.create_limit_order(OrderSide.sell, pair, amount, price, *params)

    def create_limit_order(self, order_side, pair, amount, price, *params):
        attempt_msg = LIMIT_BUY_ORDER_ATTEMPT if order_side == OrderSide.buy else LIMIT_SELL_ORDER_ATTEMPT
        err_msg = LIMIT_BUY_ORDER_ERR if order_side == OrderSide.buy else LIMIT_SELL_ORDER_ERR
        print(attempt_msg.format(self.exchange_name))
        err_msg = err_msg.format(self.exchange_name)

        if self.exchange_id == exchange_ids.bittrex:
            # Bittrex integration expects floats
            amount = float(amount)
            price = float(price)

        self.__client.verbose = True
        limit_order_method = self.__client.create_limit_buy_order if order_side == OrderSide.buy else self.__client.create_limit_sell_order
        response = make_api_limit_order_request(err_msg, limit_order_method, pair.name_for_exchange_clients, amount,
                                                price, params)
        self.__client.verbose = False
        if response is None:
            return

        standardized = Order.standardize_exchange_data(response, self.exchange_id)

        # additional exchange data
        standardized = self.add_missing_create_limit_order_fields(price=price, amount=amount, pair=pair,
                                                                  order_data=standardized)
        return Order(**standardized)

    def add_missing_create_limit_order_fields(self, pair, price, amount, order_data):
        """
        Bittrex doesn't return certain fields with the create_limit_*_order response,
        so populate them so that the order data is saved.
        Args:
            order_data dict: order data
            pair:
            price:
            amount:

        Returns:

        """
        order_data['exchange_id'] = self.exchange_id
        order_data['base'] = pair.base
        order_data['quote'] = pair.quote
        order_data['amount'] = order_data.get('amount') if order_data.get('amount') is not None else FinancialData(
            amount)
        order_data['price'] = order_data.get('price') if order_data.get('price') is not None else FinancialData(price)

        # Binance sets the following fields. Bittrex doesn't.
        if self.exchange_id == exchange_ids.bittrex:
            # Bittrex doesn't return this data, so assume 0
            order_data['filled'] = zero
            order_data['remaining'] = FinancialData(amount)
        return order_data

    def fetch_closed_orders(self, symbol=None):
        return self.__client.fetch_closed_orders(symbol)

    def fetch_order(self, order_id=None, symbol=None):
        return self.__client.fetch_order(id=order_id, symbol=symbol)

    def fetch_orders(self, symbol=None):
        return self.__client.fetch_orders(symbol)

    def fetch_open_orders(self, symbol=None):
        """

        Args:
            symbol: should be passed as a parameter when possible because on Binance,
                fetching open orders without specifying a symbol is rate-limited to one call per 152 seconds.

        Returns:

        """
        self.__open_orders = {}
        self.__client.load_markets()
        try:
            self.__client.verbose = True
            order_data_list = make_api_request(
                api_request_msgs.OPEN_ORDERS_ERR.format(self.exchange_name), self.__client.fetch_open_orders, symbol)
            self.__client.verbose = False
        except ccxt.OrderNotFound:
            order_data_list = None

        if order_data_list is None:
            return self.__open_orders

        for order_data in order_data_list:
            standardized = Order.standardize_exchange_data(order_data, self.exchange_id)
            order = Order(**standardized)
            self.__open_orders[order.order_index] = order

        return self.__open_orders

    def get_open_order(self, order_index):
        return self.__open_orders.get(order_index)

    ###########################################
    # Account State
    ###########################################
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
            quote FinancialData:
            base FinancialData:
            quote_price: price of quote, in base currency

        Returns FinancialData: base sale value post fees, in the quote
        """
        base_withdrawal_fee_in_quote = self.convert_currency_withdrawal_fee(base, quote_price)
        # the "quote_price" variable cancels out mathematically
        return self.get_balance(quote) / (one + self.trade_fee) - base_withdrawal_fee_in_quote

    def currency_purchased_value_post_fees(self, currency, currency_price, base_amount):
        """
        How much currency the exchange could buy and withdraw after trade and withdrawal fees
        Args:
            currency_price: price of currency
            currency:
            base_amount:
        """
        return base_amount / (currency_price * (one + self.trade_fee)) - self.withdrawal_fee_for_currency(
            currency)

    def withdrawal_fee_for_currency(self, currency):
        currency = standardizers.currency(currency)
        # values in dataframe are in float type, which is not compatible with the FinancialData type (Decimal)
        if currency.upper() in self.__withdrawal_fees.index:
            return FinancialData(self.__withdrawal_fees.at[currency.upper(), 'withdrawal_fee'])
        else:
            print('ERROR - withdrawal fee not found for currency {0} and exchange {1}'.format(currency.upper(),
                                                                                              self.exchange_name))
            return zero

    ###########################################
    # Trading - Funding
    ###########################################

    def fetch_deposit_destination(self, currency, params={}):
        try:
            response = self.__client.fetch_deposit_address(currency)
            # Make 'status' parameter consistent across exchanges.
            if response['tag'] == '':
                response['tag'] = None
            return DepositDestination(response['address'], response['tag'], response['status'])
        except ExchangeError as ex:
            if DepositDestination.offline_status in str(ex):
                return DepositDestination(None, None, DepositDestination.offline_status)
            raise ex

    def withdraw_all(self, currency, address, tag=None, params={}):
        """
        Convenience method to withdraw all of a currency.
        Args:
            currency:
            address:
            tag:
            params:

        Returns:

        """
        amount = self.get_balance(currency)
        return self.withdraw(currency=currency, amount=amount, address=address, tag=tag,
                             params=params)

    def withdraw(self, currency, amount, address, tag=None, params={}):
        """
        https://github.com/ccxt/ccxt/wiki/Manual#withdraw
        Args:
            currency:
            amount:
            address:
            tag:
            params:

        Returns:

        """
        return self.__client.withdraw(currency=currency, amount=amount, address=address, tag=tag, params=params)

    ###########################################
    # Account state
    ###########################################

    def get_balance(self, currency):
        """
         Returns free balance from balances data structure. Does not cause a HTTP request so the Balance returned
         may be outdated.
         Args:
             currency: currency whose Balance will be fetched

         Returns FinancialData: currency balance free to trade
         """
        balance = self.__balances.get(currency)
        return balance.free if balance is not None else zero

    def fetch_balances(self) -> Dict[str, Balance]:
        """
        example Binance API response:
        {'info': {'balances': [{'asset': 'BTC', 'free': '0.00000000', 'locked': '0.00000000'}
        :return:
        """
        self.__balances = {}

        data = make_api_request(api_request_msgs.BALANCE_ERR.format(self.exchange_name), self.__client.fetch_balance)

        if self.exchange_id == exchange_ids.bittrex:
            balances = data.get('info')
            currency_prop_name = 'Currency'
            free_prop_name = 'Available'
            locked_prop_name = 'Pending'
        else:
            balances = data.get('info').get('balances')
            currency_prop_name = 'asset'
            free_prop_name = 'free'
            locked_prop_name = 'locked'

        # Kraken example API response (Kraken is unused for now):
        # {'info': [{'Currency': 'BTC', 'Balance': 0.0, 'Available': 0.0, 'Pending': 0.0, 'CryptoAddress': '1FdGHn9b9dzwfEfxnjK4DJoy45DnqzaQcF'}, ...]}
        #

        if balances is None:
            return self.__balances

        for balance in balances:
            currency = balance.get(currency_prop_name)
            if currency is None:
                continue
            free = FinancialData(balance.get(free_prop_name, zero))
            locked = FinancialData(balance.get(locked_prop_name, zero))
            total = free + locked
            if total == zero:
                continue
            kwargs = {
                'db_id': None,
                'currency': currency,
                'exchange_id': self.exchange_id,
                'free': free,
                'locked': locked,
                'total': total,
                'version': 0,
                'event_time': None,
                'processing_time': utc_timestamp(),
            }
            self.__balances[currency] = Balance(**kwargs)

        return self.__balances

    ###########################################
    # Market state
    ###########################################
    def fetch_market_symbols(self):
        """
        fetch_markets.py was used to get a list of pairs for each exchange, and those lists were manually copied into
        the subclass implementations of this method.
        :return:
        """
        return exchange_pairs.all_exchanges.get(self.exchange_id)

    def fetch_latest_tickers(self):
        tickers = make_api_request(
            api_request_msgs.TICKER_ERR.format(self.exchange_name), self.__client.fetch_tickers)

        if tickers is None:
            return

        ticker_instances = []
        for ticker in tickers.values():
            pair_name, ticker_instance = Ticker.from_exchange_data(ticker, self.exchange_id, Ticker.current_version)
            if ticker_instance is None or ticker_instance.base is None or ticker_instance.quote is None:
                continue
            ticker_instances.append(ticker_instance)
            self.__tickers[pair_name] = ticker_instance

        return ticker_instances

    def get_tickers(self) -> Dict[str, Ticker]:
        return self.__tickers

    def get_ticker(self, pair_name):
        return self.__tickers.get(pair_name)

    def load_markets(self):
        return self.__client.load_markets()

    @staticmethod
    def id():
        pass

    @staticmethod
    def name():
        pass
