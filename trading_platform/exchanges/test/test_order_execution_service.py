import unittest
from collections import Set
from copy import copy
from logging import Logger
from typing import Dict, List

from nose.tools import eq_

from trading_platform.core.test.util_methods import eq_ignore_certain_fields
from trading_platform.exchanges.backtest.backtest_service import BacktestService
from trading_platform.exchanges.data.enums import exchange_ids
from trading_platform.exchanges.data.enums.order_side import OrderSide
from trading_platform.exchanges.data.enums.order_status import OrderStatus
from trading_platform.exchanges.data.enums.order_type import OrderType
from trading_platform.exchanges.data.financial_data import FinancialData

from trading_platform.exchanges.data.order import Order
from trading_platform.exchanges.exchange_service_abc import ExchangeServiceAbc

from trading_platform.core.services.logging_service import LoggingService
from trading_platform.exchanges.backtest import backtest_subclasses
from trading_platform.exchanges.order_execution_service import OrderExecutionService
from trading_platform.storage.daos.order_dao import OrderDao
from trading_platform.storage.sql_alchemy_engine import SqlAlchemyEngine
from trading_platform.utils.datetime_operations import utc_timestamp


class TestOrderExecutionService(unittest.TestCase):
    order_fields_to_ignore = [
        'processing_time',
        'exchange_order_id',
        'order_status'
    ]

    @classmethod
    def setUpClass(cls):
        cls.backtest_services = backtest_subclasses.instantiate()
        cls.engine = SqlAlchemyEngine.local_engine_maker()
        cls.engine.initialize_tables()
        cls.session = cls.engine.scoped_session_maker()
        cls.order_dao = OrderDao()
        cls.logger: Logger = LoggingService.set_logger()

        cls.processing_time: float = utc_timestamp()
        cls.strategy_execution_id = str(utc_timestamp())
        cls.base_order: Order = Order(**{
            # app metadata
            'processing_time': cls.processing_time,
            'version': Order.current_version,

            'strategy_execution_id': cls.strategy_execution_id,

            # exchange-related metadata
            'exchange_id': exchange_ids.bittrex,
            'order_type': OrderType.limit,

            # order metadata
            'base': 'USDT',
            'quote': 'NEO',
            'order_status': OrderStatus.pending,

            'amount': FinancialData(5),
            'price': FinancialData(50)
        })

    def setUp(self):
        self.backtest_services: Dict[id, BacktestService] = backtest_subclasses.instantiate()
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
        buy_order: Order = copy(self.base_order)
        buy_order.order_side = OrderSide.buy
        self.execute_order(buy_order)

    def execute_order(self, order: Order):
        bittrex = self.backtest_services[exchange_ids.bittrex]
        bittrex.deposit_immediately('USDT', FinancialData(1000))
        order_set: Set[Order] = {order}
        order_executed: Order = self.order_execution_service.execute_order(order, self.session, write_pending_order=True)

        # compare order with order returned from exchange
        eq_ignore_certain_fields(order_executed, order, fields_to_ignore=self.order_fields_to_ignore)
        assert(order_executed.exchange_order_id is not None)
        eq_(order_executed.order_status, OrderStatus.open)

        # compare order with order returned from the database
        session, orders = self.order_dao.fetch_all(self.session)
        order_from_db = orders[0]
        eq_ignore_certain_fields(order_from_db, order, fields_to_ignore=['db_id', 'created_at'])
