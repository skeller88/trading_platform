"""
Test exchange live functionality. These tests depend on the exchange having a nonzero USDT and BTC balance.

Exchanges won't allow for multiple accounts per exchange. So, the same exchange has to be used for trading
and testing. This creates some trickiness, for example, when asserting the number of open orders is as expected,
the number of open orders could vary depending on which production orders were placed.
"""
import unittest
from time import sleep
from typing import Dict, Callable, List, Optional

import pandas
from nose.tools import eq_, assert_true, assert_greater, assert_almost_equals
from trading_platform.exchanges.live.binance_live_service import BinanceLiveService

from trading_platform.core.test.data import Defaults
from trading_platform.core.test.util_methods import disable_debug_logging, eq_ignore_certain_fields
from trading_platform.exchanges.data.balance import Balance
from trading_platform.exchanges.data.enums import exchange_ids
from trading_platform.exchanges.data.enums.order_side import OrderSide
from trading_platform.exchanges.data.enums.order_status import OrderStatus
from trading_platform.exchanges.data.enums.order_type import OrderType
from trading_platform.exchanges.data.financial_data import zero, one, FinancialData
from trading_platform.exchanges.data.order import Order
from trading_platform.exchanges.data.pair import Pair
from trading_platform.exchanges.data.utils import check_required_fields
from trading_platform.exchanges.live.kucoin_live_service import KucoinLiveService
from trading_platform.exchanges.live.live_subclasses import exchange_service_credentials_for_exchange, \
    exchange_credentials_param, get_all_live_exchange_service_credentials
from trading_platform.storage.daos.balance_dao import BalanceDao
from trading_platform.storage.sql_alchemy_engine import SqlAlchemyEngine


class TestLiveExchangeService(unittest.TestCase):
    __test__ = False  # important, makes sure tests are not run on base class

    # Uncomment this line and one of the live_service_class definition lines to run a specific test of a specific
    # exchange
    # __test__ = True
    # live_service_class = KucoinLiveService

    @classmethod
    def setUpClass(cls):
        # Each inheritor of this class will set these values
        cls.live_service_class = None
        cls.live_service_class = BinanceLiveService
        cls.xrp_tag_len = None
        # Bittrex in particular has slow consistency and takes a second or more for changes to be persisted.
        cls.sleep_sec_consistency = 4

        disable_debug_logging()
        cls.pair = Pair(base='USDT', quote='BTC')
        cls.engine = SqlAlchemyEngine.local_engine_maker()
        cls.engine.initialize_tables()
        cls.session = cls.engine.scoped_session_maker()
        cls.balance_dao = BalanceDao()
        cls.credentials = get_all_live_exchange_service_credentials('exchange_credentials')
        cls.withdrawal_fees = pandas.DataFrame(
            {'currency': cls.pair.base, 'withdrawal_fee': Defaults.base_withdrawal_fee},
            {'currency': cls.pair.quote, 'withdrawal_fee': Defaults.quote_withdrawal_fee}
        )

    def setUp(self):
        """
        Avoid rate limiting.
        Returns:

        """
        sleep(5)
        credentials_for_exchange: Dict[str, str] = self.credentials.get(self.live_service_class.exchange_id)
        self.service = self.live_service_class(credentials_for_exchange.get('key'),
                                               credentials_for_exchange.get('secret'),
                                               withdrawal_fees=self.withdrawal_fees)

    def tearDown(self):
        self.balance_dao.delete_all(session=self.session)
        self.session.commit()
        self.session.close_all()

    @classmethod
    def tearDownClass(cls):
        cls.engine.drop_tables()

    def test_fetch_deposit_destination(self):
        deposit_destination = self.service.fetch_deposit_destination('ETH', {})
        eq_(len(deposit_destination.address), 42)
        assert_true(deposit_destination.address.startswith('0x'))
        eq_(deposit_destination.status, 'ok')

        if self.live_service_class.exchange_id == exchange_ids.kucoin:
            eq_(len(deposit_destination.tag), 24)
        else:
            eq_(deposit_destination.tag, None)

    def test_fetch_deposit_destination_with_tag(self):
        if self.live_service_class.exchange_id == exchange_ids.kucoin:
            return

        deposit_destination = self.service.fetch_deposit_destination('XRP', {})

        eq_(len(deposit_destination.address), 34)
        eq_(deposit_destination.status, 'ok')
        eq_(len(deposit_destination.tag), self.xrp_tag_len)

    def test_fetch_balances(self):
        balance: Balance = self.service.get_balance(self.pair.base)
        eq_(balance.free, zero)
        self.service.fetch_balances()
        base_balance: Balance = self.service.get_balance(self.pair.base)
        assert (base_balance is not None)
        assert_greater(base_balance.free, zero)

    ###########################################
    # Market state
    ###########################################
    def test_fetch_latest_tickers(self):
        eq_(len(self.service.get_tickers()), 0)
        self.service.fetch_latest_tickers()
        assert_greater(len(self.service.get_tickers()), 250)

        ticker = self.service.get_ticker(self.pair.name)
        check_required_fields(ticker)
        eq_(ticker.base, self.pair.base)
        eq_(ticker.quote, self.pair.quote)

    def test_load_markets(self):
        markets = self.service.load_markets()
        if self.service.exchange_id == exchange_ids.gdax:
            assert_greater(len(markets), 10)
        else:
            assert_greater(len(markets), 200)

    def validate_buy_order_crud(self, fields_to_ignore, decimal_comparison_precision: Optional[int]):
        """
         Should be able to place orders, fetch open orders, and cancel orders.

         Assumes that the exchange has BTC and USDT balances, each balance > $30 which is the trading minimum.

         There's no way to run this test with test orders, so create sell orders with very high prices and buy
         orders with very low prices.

         Returns:

         """
        self.service.fetch_latest_tickers()
        self.service.fetch_balances()
        quote_ticker = self.service.get_ticker(self.pair.name)
        quote_buy_price = quote_ticker.bid * (one - FinancialData(.2))

        # TODO - because of FinancialData rounding, not enough funds may be available. Figure out a better way to ake sure enough funds are available.
        buy_amount = self.service.get_balance(self.pair.base).free / quote_buy_price * FinancialData(.95)
        buy_order_kwargs: Dict = {
            'amount': buy_amount,
            'price': quote_buy_price,

            'order_side': OrderSide.buy,
            # The following Order.financial_data_fields are not populated by the exchange response
            'remaining': buy_amount,
            'filled': zero,
        }

        self.validate_order_crud(buy_order_kwargs, fields_to_ignore=fields_to_ignore,
                                 decimal_comparison_precision=decimal_comparison_precision)

    def validate_sell_order_crud(self, fields_to_ignore: List[str], decimal_comparison_precision: Optional[int]):
        """
         Should be able to place orders, fetch open orders, and cancel orders.

         Assumes that the exchange has BTC and USDT balances, each balance > $30 which is the trading minimum.

         There's no way to run this test with test orders, so create sell orders with very high prices and buy
         orders with very low prices.

         Returns:

         """
        self.service.fetch_latest_tickers()
        self.service.fetch_balances()
        quote_ticker = self.service.get_ticker(self.pair.name)
        quote_sell_price = quote_ticker.ask * (one + FinancialData(.2))

        # TODO - because of FinancialData rounding, not enough funds may be available. Figure out a better way to ake sure enough funds are available.
        sell_amount = self.service.get_balance(self.pair.quote).free * (FinancialData(.95))
        sell_order_kwargs: Dict = {
            'amount': sell_amount,
            'price': quote_sell_price,

            'order_side': OrderSide.sell,
            # The following Order.financial_data_fields are not populated by the exchange response
            'remaining': sell_amount,
            'filled': zero,
        }

        self.validate_order_crud(sell_order_kwargs, fields_to_ignore=fields_to_ignore,
                                 decimal_comparison_precision=decimal_comparison_precision)

    def validate_order_crud(self, order_kwargs, fields_to_ignore: List[str],
                            decimal_comparison_precision: Optional[int]):
        """
          Should be able to place orders, fetch open orders, and cancel orders.

          Assumes that the exchange has BTC and USDT balances, each balance > $30 which is the trading minimum.

          There's no way to run this test with test orders, so create sell orders with very high prices and buy
          orders with very low prices.

          Returns:

          """
        self.service.fetch_latest_tickers()

        base_order_kwargs: Dict = {
            'base': self.pair.base,
            'quote': self.pair.quote,

            'exchange_id': self.service.exchange_id,
            'order_status': OrderStatus.pending,
            'order_type': OrderType.limit,
        }

        base_order_kwargs.update(order_kwargs)
        order: Order = Order(**base_order_kwargs)
        exchange_method: Callable = self.service.create_limit_buy_order if order.order_side == OrderSide.buy else self.service.create_limit_sell_order
        open_order = exchange_method(order=order)

        # compare order with open_order
        eq_ignore_certain_fields(order, open_order, fields_to_ignore=fields_to_ignore)

        if decimal_comparison_precision is not None:
            for field in Order.financial_data_fields:
                assert_almost_equals(getattr(order, field), getattr(open_order, field),
                                     places=decimal_comparison_precision)

        # same fields for pending buy and sell orders
        check_required_fields(order)

        # same fields for opened buy and sell orders
        eq_(order.exchange_id, self.service.exchange_id)
        eq_(order.order_type, OrderType.limit)
        eq_(order.base, self.pair.base)
        eq_(order.quote, self.pair.quote)

        # The following fields are different between an open order and a pending order:
        # 'exchange_order_id',
        assert (order.exchange_order_id is None)
        assert (open_order.exchange_order_id is not None)

        # 'order_status',
        eq_(order.order_status, OrderStatus.pending)
        eq_(open_order.order_status, OrderStatus.open)

        # 'app_create_timestamp',
        assert_greater(open_order.app_create_timestamp, order.app_create_timestamp)

        sleep(self.sleep_sec_consistency)

        open_orders: Dict[str, Order] = self.service.fetch_open_orders(
            Pair(base=self.pair.base, quote=self.pair.quote))
        # order - '0_BTC_USDT_0_5105.60800_0.02766'
        # open_order - '0_BTC_USDT_0_5105.61000_0.02766'

        # test suite
        # order - '0_BTC_USDT_0_5089.136_0.028'
        # open_order - '0_BTC_USDT_0_5089.140_0.028'

        # single test
        # order - '0_BTC_USDT_0_5079.08000_0.02781'
        # open_order - '0_BTC_USDT_0_5079.08000_0.02781'
        assert_true(len(open_orders) == 1)

        # '0_BTC_USDT_0_5096_00000_0_02771'
        open_order = self.service.get_order(order.order_id)
        check_required_fields(open_order)

        # The exchange data returned by the create_limit call is different from the
        # exchange data returned by the fetch_open_orders call.
        fields_to_ignore.append('exchange_timestamp')
        eq_ignore_certain_fields(open_order, order, fields_to_ignore=fields_to_ignore)
        assert (open_order.exchange_timestamp is not None)

        if decimal_comparison_precision is not None:
            for field in Order.financial_data_fields:
                assert_almost_equals(getattr(order, field), getattr(open_order, field),
                                     places=decimal_comparison_precision)

        cancelled_buy_order = self.service.cancel_order(order=open_order)
        eq_(cancelled_buy_order.order_id, open_order.order_id)
        eq_(cancelled_buy_order.order_status, OrderStatus.cancelled)

        sleep(self.sleep_sec_consistency)

        open_orders: Dict[str, Order] = self.service.fetch_open_orders(
            Pair(base=self.pair.base, quote=self.pair.quote))
        eq_(len(open_orders), 0)

        open_order = self.service.get_order(order.order_id)
        assert (open_order is None)

    @staticmethod
    def fetch_open_orders_for_order_instances(exchange_service, order_instances):
        """

        Args:
            order_instances list(Order):

        Returns:

        """
        open_orders = {}

        for order in order_instances:
            open_orders.update(exchange_service.fetch_open_orders(Pair(base=order.base, quote=order.quote)))

        return open_orders
