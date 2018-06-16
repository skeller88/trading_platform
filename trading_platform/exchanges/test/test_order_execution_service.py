import random
import unittest
from copy import copy
from logging import Logger
from time import sleep
from typing import Dict, Set, List
from unittest.mock import MagicMock

from nose.tools import eq_, assert_greater
from trading_platform.exchanges.exchange_service_abc import ExchangeServiceAbc

from trading_platform.core.services.logging_service import LoggingService
from trading_platform.core.test.util_methods import eq_ignore_certain_fields
from trading_platform.exchanges.backtest import backtest_subclasses
from trading_platform.exchanges.backtest.backtest_exchange_service import BacktestExchangeService
from trading_platform.exchanges.data.enums import exchange_ids
from trading_platform.exchanges.data.enums.order_side import OrderSide
from trading_platform.exchanges.data.enums.order_status import OrderStatus
from trading_platform.exchanges.data.enums.order_type import OrderType
from trading_platform.exchanges.data.financial_data import FinancialData, two
from trading_platform.exchanges.data.order import Order
from trading_platform.exchanges.order_execution_service import OrderExecutionService
from trading_platform.storage.daos.order_dao import OrderDao
from trading_platform.storage.sql_alchemy_engine import SqlAlchemyEngine
from trading_platform.utils.datetime_operations import utc_timestamp


class TestOrderExecutionService(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = SqlAlchemyEngine.local_engine_maker()
        cls.engine.initialize_tables()
        cls.session = cls.engine.scoped_session_maker()
        cls.order_dao = OrderDao()
        cls.logger: Logger = LoggingService.set_logger()

        cls.processing_time: float = utc_timestamp()
        cls.strategy_execution_id = str(utc_timestamp())
        cls.base: str = 'USDT'
        cls.quote: str = 'ETH'
        cls.quote_amount = FinancialData(5)
        cls.quote_price = FinancialData(2)

        cls.base_order_kwargs: Dict = {
            # app metadata
            'processing_time': cls.processing_time,
            'version': Order.current_version,

            'strategy_execution_id': cls.strategy_execution_id,

            # exchange-related metadata
            'exchange_id': exchange_ids.bittrex,
            'order_type': OrderType.limit,

            # order metadata
            'base': cls.base,
            'quote': cls.quote,
            'order_status': OrderStatus.pending,

            'amount': cls.quote_amount,
            'price': cls.quote_price
        }

    def setUp(self):
        self.backtest_services: Dict[id, BacktestExchangeService] = backtest_subclasses.instantiate()
        self.bittrex = self.backtest_services[exchange_ids.bittrex]

        self.order_execution_service: OrderExecutionService = OrderExecutionService(**{
            'logger': self.logger,
            'exchanges_by_id': self.backtest_services,
            'order_dao': self.order_dao,
            'multithreaded': False,
            'num_order_status_checks': 1,
            'sleep_time_sec_between_order_checks': 0
        })

    def tearDown(self):
        self.order_dao.delete_all(session=self.session)
        self.session.commit()
        self.session.close_all()

    @classmethod
    def tearDownClass(cls):
        cls.engine.drop_tables()

    ########################
    # Execute buy order
    ########################

    def test_execute_buy_order(self):
        # multiple by two to make sure there's enough base
        self.bittrex.deposit_immediately(self.base, self.quote_amount * self.quote_price * two)

        self.execute_order(self.buy_order_instance())

    def test_execute_buy_order_write_pending(self):
        """
        Poll to check that order has been filled, but order is still open.

        Returns:

        """
        # multiple by two to make sure there's enough base
        self.bittrex.deposit_immediately(self.base, self.quote_amount * self.quote_price * two)

        self.execute_order(self.buy_order_instance(), write_pending_order=True)

    def test_execute_buy_order_poll_status_order_open(self):
        """
        Poll to check that order has been filled, but order is still open.

        Returns:

        """
        # multiple by two to make sure there's enough base
        self.bittrex.deposit_immediately(self.base, self.quote_amount * self.quote_price * two)

        self.execute_order(self.buy_order_instance(), check_if_order_filled=True)

    def test_execute_buy_order_poll_status_order_filled(self):
        """
        Poll to check that order has been filled, but order is still open.

        Returns:

        """
        # multiple by two to make sure there's enough base
        self.bittrex.deposit_immediately(self.base, self.quote_amount * self.quote_price * two)

        self.execute_order(self.buy_order_instance(), check_if_order_filled=True,
                           order_status_on_exchange=OrderStatus.filled)

    def test_execute_buy_order_write_pending_poll_status_order_open(self):
        """
        Poll to check that order has been filled, but order is still open.

        Returns:

        """
        # multiple by two to make sure there's enough base
        self.bittrex.deposit_immediately(self.base, self.quote_amount * self.quote_price * two)

        self.execute_order(self.buy_order_instance(), check_if_order_filled=True, write_pending_order=True)

    def test_execute_buy_order_poll_write_pending_status_order_filled(self):
        """
        Poll to check that order has been filled, and order has been filled.

        Returns:

        """
        # multiple by two to make sure there's enough base
        self.bittrex.deposit_immediately(self.base, self.quote_amount * self.quote_price * two)

        self.execute_order(self.buy_order_instance(), order_status_on_exchange=OrderStatus.filled,
                           check_if_order_filled=True, write_pending_order=True)

    def test_execute_buy_order_poll_write_pending_status_order_open(self):
        """
        Poll to check that order has been filled, and order is still open.

        Returns:

        """
        # multiple by two to make sure there's enough base
        # multiple by two to make sure there's enough base
        self.bittrex.deposit_immediately(self.base, self.quote_amount * self.quote_price * two)

        self.execute_order(self.buy_order_instance(), order_status_on_exchange=OrderStatus.open,
                           check_if_order_filled=True, write_pending_order=True)

    ########################
    # Execute sell order
    ########################

    def test_execute_sell_order(self):
        self.setup_exchange_for_sell_order(self.bittrex)
        self.execute_order(self.sell_order_instance())

    def test_execute_sell_order_write_pending(self):
        self.setup_exchange_for_sell_order(self.bittrex)

        self.execute_order(self.sell_order_instance(), write_pending_order=True)

    def test_execute_sell_order_poll_status_order_open(self):
        self.setup_exchange_for_sell_order(self.bittrex)

        self.execute_order(self.sell_order_instance(), order_status_on_exchange=OrderStatus.open,
                           check_if_order_filled=True)

    def test_execute_sell_order_poll_status_order_filled(self):
        """
        Poll to check that order has been filled, but order is still open.

        Returns:

        """
        self.setup_exchange_for_sell_order(self.bittrex)

        self.execute_order(self.sell_order_instance(), order_status_on_exchange=OrderStatus.filled,
                           check_if_order_filled=True)

    def test_execute_sell_order_write_pending_poll_status_order_open(self):
        """
        Poll to check that order has been filled, but order is still open.

        Returns:

        """
        self.setup_exchange_for_sell_order(self.bittrex)

        self.execute_order(self.sell_order_instance(), order_status_on_exchange=OrderStatus.open,
                           check_if_order_filled=True)

    def test_execute_sell_order_poll_write_pending_status_order_filled(self):
        """
        Poll to check that order has been filled, and order has been filled.

        Returns:

        """
        # multiple by two to make sure there's enough base
        self.setup_exchange_for_sell_order(self.bittrex)

        self.execute_order(self.sell_order_instance(), order_status_on_exchange=OrderStatus.filled,
                           check_if_order_filled=True, write_pending_order=True)

    def test_execute_sell_order_poll_write_pending_status_order_open(self):
        """
        Poll to check that order has been filled, and order is still open.

        Returns:

        """
        # multiple by two to make sure there's enough base
        self.setup_exchange_for_sell_order(self.bittrex)

        self.execute_order(self.sell_order_instance(), order_status_on_exchange=OrderStatus.open,
                           check_if_order_filled=True, write_pending_order=True)

    @unittest.skip('This test fails because the session gets closed unexpectedly. Figure out why.')
    # I would expect this test to pass because I'm using scoped sessions.
    # https://stackoverflow.com/questions/6297404/multi-threaded-use-of-sqlalchemy
    def test_execute_orders_multithreaded(self):
        self.execute_orders(True)

    def test_execute_orders(self):
        self.execute_orders(False)

    def execute_orders(self, multithreaded):
        self.order_execution_service: OrderExecutionService = OrderExecutionService(
            logger=self.logger, order_dao=self.order_dao, exchanges_by_id=self.backtest_services,
            multithreaded=multithreaded)

        # multiple by two to make sure there's enough base
        self.bittrex.deposit_immediately(self.base, self.quote_amount * self.quote_price * two)
        self.bittrex.deposit_immediately(self.quote, self.quote_amount)
        self.bittrex.set_buy_price('{0}_{1}'.format(self.quote, self.base), self.quote_price)
        self.bittrex.set_usdt_tickers({
            'USDT': FinancialData(1)
        })

        buy_order_kwargs: Dict = copy(self.base_order_kwargs)
        buy_order_kwargs['order_side'] = OrderSide.buy
        buy_order = Order(**buy_order_kwargs)

        sell_order_kwargs: Dict = copy(self.base_order_kwargs)
        sell_order_kwargs['order_side'] = OrderSide.sell
        sell_order: Order = Order(**sell_order_kwargs)

        order_set: Set[Order] = {buy_order, sell_order}
        executed_orders: Dict[str, Order] = self.order_execution_service.execute_order_set(order_set, self.session,
                                                                                           write_pending_order=True,
                                                                                           check_if_orders_filled=True)
        eq_(len(executed_orders.values()), len(order_set))
        eq_(len(self.order_dao.fetch_all(self.session)), len(order_set) * 2)

        # Wait for writes to happen to the database. TODO - use a callback instead
        if multithreaded:
            sleep(2)

        for order in order_set:
            order_from_db = self.order_dao.fetch_latest_with_order_id(order_id=order.order_id,
                                                                      session=self.session)
            eq_(order_from_db.order_status, OrderStatus.open)
            eq_ignore_certain_fields(order_from_db, executed_orders.get(order.order_id), fields_to_ignore=[
                'db_id',
                'created_at',
            ])

    def execute_order(self, order: Order, write_pending_order=False, order_status_on_exchange=OrderStatus.open,
                      check_if_order_filled=False):
        # check_if_order_filled causes OrderExecutionService#poll_exchange_for_order_status to be invoked, and call
        # ExchangeServiceAbc#fetch_order. A new order should be returned only if the order status has changed.
        if order_status_on_exchange != OrderStatus.open:
            order_returned_by_exchange = copy(order)
            order_returned_by_exchange.order_status = order_status_on_exchange
            order_returned_by_exchange.exchange_order_id = self.bittrex.new_exchange_order_id()
            self.bittrex.fetch_order = MagicMock(return_value=order_returned_by_exchange)

        order_snapshot: Order = self.order_execution_service.execute_order(order, self.session,
                                                                           write_pending_order=write_pending_order,
                                                                           check_if_order_filled=check_if_order_filled)
        # compare order with order returned from exchange
        eq_ignore_certain_fields(order_snapshot, order, fields_to_ignore=[
            'processing_time',
            'exchange_order_id',
            # the order_status on the exchange will be different from the original order status of "pending"
            'order_status'
        ])
        assert (order_snapshot.exchange_order_id is not None)
        eq_(order_snapshot.order_status, order_status_on_exchange)

        # compare order with order returned from the database
        orders = self.order_dao.fetch_all(self.session)

        expected_order_statuses = [OrderStatus.open]

        if write_pending_order:
            expected_order_statuses.append(OrderStatus.pending)

        if order_status_on_exchange not in expected_order_statuses:
            expected_order_statuses.append(order_status_on_exchange)

        eq_(len(orders), len(expected_order_statuses))
        actual_order_statuses: List[OrderStatus] = list(map(lambda x: x.order_status, orders))
        for order_status in expected_order_statuses:
            assert (order_status in actual_order_statuses)

        latest_order_from_db = self.order_dao.fetch_latest_with_order_id(order_id=order.order_id, session=self.session)
        eq_ignore_certain_fields(latest_order_from_db, order_snapshot, fields_to_ignore=[
            'db_id',
            'created_at',
        ])
        assert (latest_order_from_db.db_id is not None)
        assert (latest_order_from_db.created_at is not None)

    def buy_order_instance(self) -> Order:
        buy_order_kwargs: Dict = copy(self.base_order_kwargs)
        buy_order_kwargs['order_side'] = OrderSide.buy
        return Order(**buy_order_kwargs)

    def sell_order_instance(self) -> Order:
        sell_order_kwargs: Dict = copy(self.base_order_kwargs)
        sell_order_kwargs['order_side'] = OrderSide.sell
        return Order(**sell_order_kwargs)

    def setup_exchange_for_sell_order(self, exchange: BacktestExchangeService):
        exchange.deposit_immediately(self.quote, self.quote_amount)
        exchange.set_usdt_tickers({
            'USDT': FinancialData(1)
        })
        exchange.set_buy_price('{0}_{1}'.format(self.quote, self.base), self.quote_price)