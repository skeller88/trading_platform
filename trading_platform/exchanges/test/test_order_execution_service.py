import unittest
from copy import copy
from logging import Logger
from time import sleep
from typing import Dict, Set, List

from nose.tools import eq_, assert_greater

from trading_platform.core.services.logging_service import LoggingService
from trading_platform.core.test.util_methods import eq_ignore_certain_fields
from trading_platform.exchanges.backtest import backtest_subclasses
from trading_platform.exchanges.backtest.backtest_service import BacktestService
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
        self.backtest_services: Dict[id, BacktestService] = backtest_subclasses.instantiate()
        self.bittrex = self.backtest_services[exchange_ids.bittrex]
        self.order_execution_service: OrderExecutionService = OrderExecutionService(
            logger=self.logger, order_dao=self.order_dao, exchanges_by_id=self.backtest_services,
            multithreaded=False)

    def tearDown(self):
        self.order_dao.delete_all(session=self.session)
        self.session.commit()
        self.session.close_all()

    @classmethod
    def tearDownClass(cls):
        cls.engine.drop_tables()

    def test_execute_buy_order(self):
        # multiple by two to make sure there's enough base
        self.bittrex.deposit_immediately(self.base, self.quote_amount * self.quote_price * two)

        buy_order_kwargs: Dict = copy(self.base_order_kwargs)
        buy_order_kwargs['order_side'] = OrderSide.buy
        buy_order = Order(**buy_order_kwargs)
        self.execute_order(buy_order, True)

    def test_execute_buy_order_write_pending(self):
        # multiple by two to make sure there's enough base
        self.bittrex.deposit_immediately(self.base, self.quote_amount * self.quote_price * two)

        buy_order_kwargs: Dict = copy(self.base_order_kwargs)
        buy_order_kwargs['order_side'] = OrderSide.buy
        buy_order = Order(**buy_order_kwargs)
        self.execute_order(buy_order, False)

    def test_execute_sell_order_write_pending(self):
        self.bittrex.deposit_immediately(self.quote, self.quote_amount)
        self.bittrex.set_usdt_tickers({
            'USDT': FinancialData(1)
        })
        self.bittrex.set_buy_price('{0}_{1}'.format(self.quote, self.base), self.quote_price)

        sell_order_kwargs: Dict = copy(self.base_order_kwargs)
        sell_order_kwargs['order_side'] = OrderSide.sell
        sell_order: Order = Order(**sell_order_kwargs)
        self.execute_order(sell_order, True)

    def test_execute_sell_order(self):
        self.bittrex.deposit_immediately(self.quote, self.quote_amount)
        self.bittrex.set_usdt_tickers({
            'USDT': FinancialData(1)
        })
        self.bittrex.set_buy_price('{0}_{1}'.format(self.quote, self.base), self.quote_price)

        sell_order_kwargs: Dict = copy(self.base_order_kwargs)
        sell_order_kwargs['order_side'] = OrderSide.sell
        sell_order: Order = Order(**sell_order_kwargs)
        self.execute_order(sell_order, False)

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
                                                                                           write_pending_order=True)
        eq_(len(executed_orders.values()), len(order_set))
        orders = self.order_dao.fetch_all(self.session)
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

    def execute_order(self, order: Order, write_pending_order=True):
        order_executed: Order = self.order_execution_service.execute_order(order, self.session,
                                                                           write_pending_order=write_pending_order)
        # compare order with order returned from exchange
        eq_ignore_certain_fields(order_executed, order, fields_to_ignore=[
            'processing_time',
            'exchange_order_id',
            'order_status'
        ])
        assert (order_executed.exchange_order_id is not None)
        assert_greater(order_executed.processing_time, order.processing_time)
        eq_(order_executed.order_status, OrderStatus.open)

        # compare order with order returned from the database
        orders = self.order_dao.fetch_all(self.session)

        num_orders_written = 2 if write_pending_order else 1
        expected_order_statuses = [OrderStatus.pending, OrderStatus.open] if write_pending_order else [OrderStatus.open]
        eq_(len(orders), num_orders_written)
        actual_order_statuses: List[OrderStatus] = list(map(lambda x: x.order_status, orders))
        for order_status in expected_order_statuses:
            assert (order_status in actual_order_statuses)

        open_order_from_db = self.order_dao.fetch_latest_with_order_id(order_id=order.order_id, session=self.session)
        eq_ignore_certain_fields(open_order_from_db, order_executed, fields_to_ignore=[
            'db_id',
            'created_at',
        ])
        assert (open_order_from_db.db_id is not None)
        assert (open_order_from_db.created_at is not None)
