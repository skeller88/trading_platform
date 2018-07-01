from typing import Dict, Optional, List

import ccxt
from ccxt import ExchangeError, InvalidOrder

from trading_platform.core.constants import exchange_pairs
from trading_platform.exchanges.data import standardizers
from trading_platform.exchanges.data.balance import Balance
from trading_platform.exchanges.data.deposit_destination import DepositDestination
from trading_platform.exchanges.data.enums import exchange_ids
from trading_platform.exchanges.data.enums.order_side import OrderSide
from trading_platform.exchanges.data.financial_data import FinancialData, zero, one
from trading_platform.exchanges.data.order import Order
from trading_platform.exchanges.data.pair import Pair
from trading_platform.exchanges.data.ticker import Ticker
from trading_platform.exchanges.exchange_service_abc import ExchangeServiceAbc
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
        self.__orders= {}
        self.__tickers = {}
        self.__withdrawal_fees = withdrawal_fees

    ###########################################
    # Trading - Orders
    ###########################################

    def cancel_order(self, order) -> Optional[Order]:
        """
        :param order: str
        :param pair: Pair
        :return:
        """
        if self.exchange_id == exchange_ids.binance:
            order.exchange_order_id = int(order.exchange_order_id)

        if self.exchange_id == exchange_ids.kucoin:
            params: Dict[str, str] = {
                'type': 'BUY' if order.order_side == OrderSide.buy else 'SELL'
            }
        else:
            params: Dict[str, str] = {}

        pair: Pair = Pair(base=order.base, quote=order.quote)
        try:
            response = make_api_request(self.__client.cancel_order, order.exchange_order_id, pair.name_for_exchange_clients, params)
        except InvalidOrder as ex:
            if 'ORDER_NOT_OPEN' in ex.args[0]:
                return None
            else:
                raise ex

        if response:
            return order.copy_updated_with_cancel_order_exchange_response(response)

        raise Exception('Order was not cancelled', response)

    def create_limit_buy_order(self, order, params={}) -> Optional[Order]:
        if order.order_side != OrderSide.buy:
            raise Exception('OrderSide != OrderSide.buy')

        return self.create_limit_order(order, **params)

    def create_limit_sell_order(self, order, params={}) -> Optional[Order]:
        if order.order_side != OrderSide.sell:
            raise Exception('OrderSide != OrderSide.sell')
        return self.create_limit_order(order, **params)

    def create_limit_order(self, order: Order, **params) -> Optional[Order]:
        # These integrations expect floats
        if self.exchange_id in [exchange_ids.bittrex, exchange_ids.kucoin]:
            amount = float(order.amount)
            price = float(order.price)
        else:
            amount = order.amount
            price = order.price

        # Some exchanges allow that id to be sent with a create order request, and it's
        # useful for recording the id of an order in the app database before attempting an order. Then if the app
        # fails and restarts, it can look up the state of an order on the exchange with the client_order_id.
        # In order for this record keeping method to work, Order#from_fetch_order_exchange_response sets "order_id"
        # to the "clientOrderId" property of the exchange response.
        if self.exchange_id == exchange_ids.binance:
            params['newClientOrderId'] = order.order_id

        pair: Pair = Pair(base=order.base, quote=order.quote)

        limit_order_method = self.__client.create_limit_buy_order if order.order_side == OrderSide.buy else self.__client.create_limit_sell_order
        response = make_api_limit_order_request(limit_order_method, pair.name_for_exchange_clients, amount,
                                                price, params)

        if response is None:
            return

        order_copy: Order = order.copy_updated_with_create_order_exchange_response(response)
        return order_copy

    def fetch_closed_orders(self, pair=None, since=None, limit=None, params={}) -> Dict[str, Order]:
        return self.__client.fetch_closed_orders(pair.name_for_exchange_clients, since, limit, params)

    def fetch_order(self, exchange_order_id=None, pair=None) -> Optional[Order]:
        if pair is None:
            symbol = None
        else:
            symbol = pair.name_for_exchange_clients

        response: Dict = make_api_request(self.__client.fetch_order, exchange_order_id, symbol)

        if response:
            order: Order = Order.from_fetch_order_exchange_response(response, self.exchange_id)
            return order

    def fetch_orders(self, pair=None):
        """
        Some exchanges, like Bittrex, haven't implemented this method.
        Args:
            pair:

        Returns:

        """
        return self.__client.fetch_orders(pair.name_for_exchange_clients)

    def fetch_open_orders(self, pair: Pair) -> Dict[str, Order]:
        """
        Fetches open orders, updates the internal orders state, and returns the open orders.

        Args:
            pair: should be passed as a parameter when possible because on Binance,
                fetching open orders without specifying a symbol is rate-limited to one call per 152 seconds.

        Returns:

        """
        self.__orders: Dict[str, Order] = {}
        try:
            order_data_list = make_api_request(self.__client.fetch_open_orders, pair.name_for_exchange_clients)
        except ccxt.OrderNotFound:
            order_data_list = None
        # price - 5081.0600000
        if order_data_list is None:
            return self.__orders

        for order_data in order_data_list:
            order: Order = Order.from_fetch_order_exchange_response(order_data, self.exchange_id)
            self.__orders[order.order_id] = order

        return self.__orders

    def get_order(self, order_id) -> Optional[Order]:
        return self.__orders.get(order_id)

    ###########################################
    # Account State
    ###########################################
    def convert_currency_withdrawal_fee(self, currency_to_convert, price_of_target_currency) -> FinancialData:
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

    def currency_sale_value_post_fees(self, quote, base, quote_price) -> FinancialData:
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

    def currency_purchased_value_post_fees(self, currency, currency_price, base_amount) -> FinancialData:
        """
        How much currency the exchange could buy and withdraw after trade and withdrawal fees
        Args:
            currency_price: price of currency
            currency:
            base_amount:
        """
        return base_amount / (currency_price * (one + self.trade_fee)) - self.withdrawal_fee_for_currency(
            currency)

    def withdrawal_fee_for_currency(self, currency) -> FinancialData:
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

    def fetch_deposit_destination(self, currency, params={}) -> DepositDestination:
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

    def get_balance(self, currency) -> Balance:
        """
         Returns free balance from balances data structure. Does not cause a HTTP request so the Balance returned
         may be outdated.
         Args:
             currency: currency whose Balance will be fetched

         Returns FinancialData: currency balance free to trade
         """
        balance: Balance = self.__balances.get(currency)
        return balance if balance is not None else Balance.instance_with_zero_value_fields()

    def fetch_balances(self) -> Dict[str, Balance]:
        self.__balances = {}

        data = make_api_request(self.__client.fetch_balance)

        if self.exchange_id == exchange_ids.bittrex:
            balances: List[Dict] = data.get('info')
            currency_prop_name = 'Currency'
            free_prop_name = 'Available'
            locked_prop_name = 'Pending'
        elif self.exchange_id == exchange_ids.gdax:
            balances: List[Dict] = data.get('info')
            currency_prop_name = 'Currency'
            free_prop_name = 'Available'
            locked_prop_name = 'Pending'
        elif self.exchange_id == exchange_ids.kucoin:
            for balance in data.get('info'):
                locked: FinancialData = FinancialData(balance.get('freezeBalance'))
                total: FinancialData = FinancialData(balance.get('balance'))
                free = max(total - locked, zero)
                currency: str = balance.get('coinType')
                kwargs = {
                    'db_id': None,
                    'currency': currency,
                    'exchange_id': self.exchange_id,
                    'free': free,
                    'locked': locked,
                    'total': total,
                    'version': 0,
                    'exchange_timestamp': None,
                    'app_create_timestamp': utc_timestamp(),
                }
                balance_instance: Balance = Balance(**kwargs)
                self.__balances[currency] = balance_instance

            return self.__balances
        else:
            balances = data.get('info').get('balances')
            currency_prop_name = 'asset'
            free_prop_name = 'free'
            locked_prop_name = 'locked'

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
                'exchange_timestamp': None,
                'app_create_timestamp': utc_timestamp(),
            }

            self.__balances[currency] = Balance(**kwargs)

        return self.__balances


    ###########################################
    # Market state
    ###########################################
    def fetch_market_symbols(self) -> List[str]:
        """
        fetch_markets.py was used to get a list of pairs for each exchange, and those lists were manually copied into
        the subclass implementations of this method.
        :return:
        """
        return exchange_pairs.all_exchanges.get(self.exchange_id)

    def fetch_latest_tickers(self) -> List[Ticker]:
        tickers = make_api_request(self.__client.fetch_tickers)

        if tickers is None:
            return []

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

    def get_ticker(self, pair_name: str) -> Optional[Ticker]:
        return self.__tickers.get(pair_name)

    def fetch_order_book(self, symbol, limit=None, params={}):
        return self.__client.fetch_order_book(symbol=symbol, limit=limit, params=params)

    def load_markets(self) -> List:
        return self.__client.load_markets()

    @staticmethod
    def id():
        pass

    @staticmethod
    def name():
        pass
