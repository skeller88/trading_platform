from abc import ABC, abstractmethod

from decimal import Decimal


class ExchangeServiceAbc(ABC):
    """
    Bridge class for any client library we use. Don't call an exchange client library directly, instead call via this
    wrapper abstract class method.
    """
    def __init__(self, key, secret, trade_fee):
        self.key = key
        self.secret = secret
        self.trade_fee = Decimal(trade_fee)

    ###########################################
    # Trading - Orders
    ###########################################

    @abstractmethod
    def cancel_order(self, order_id, pair):
        """
        :param order_id: str
        :param pair: Pair
        :return:
        """
        pass

    @abstractmethod
    def create_limit_buy_order(self, pair, amount, price, params=None):
        """
        :param pair: Pair
        :param amount: float
        :param price: float
        :param params:
        :return:
        """
        pass

    @abstractmethod
    def create_limit_sell_order(self, pair, amount, price, params=None):
        """
        :param pair: Pair
        :param amount: float
        :param price: float
        :param params:
        :return:
        """
        pass

    @abstractmethod
    def fetch_open_orders(self, symbol):
        pass

    ###########################################
    # Trading - Funding
    ###########################################

    @abstractmethod
    def fetch_deposit_destination(self, currency, params):
        """
        https://github.com/ccxt/ccxt/wiki/Manual#deposit
        Args:
            currency:
            params:

        Returns:
            For live exchange services, the destination will be an address. For backtest exchange services, the
            destination will be a backtest exchange service instance that is passed by reference, so that the instance's
            wallet can be incremented with the proper value.

        """
        pass

    @abstractmethod
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
        pass

    @abstractmethod
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
        pass

    ###########################################
    # Account state
    ###########################################

    @abstractmethod
    def get_balance(self, currency):
        pass

    @abstractmethod
    def fetch_balances(self):
        pass

    ###########################################
    # Market state
    ###########################################
    @abstractmethod
    def fetch_market_symbols(self):
        """
        fetch_markets.py was used to get a list of pairs for each exchange, and those lists were manually copied into
        the subclass implementations of this method.
        :return:
        """
        pass

    @abstractmethod
    def fetch_latest_tickers(self):
        pass

    @staticmethod
    @abstractmethod
    def id():
        pass

    @staticmethod
    @abstractmethod
    def name():
        pass

