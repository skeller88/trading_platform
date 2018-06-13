import logging
import random
import unittest
from typing import Dict

from nose.tools import eq_

from trading_platform.core.services.logging_service import LoggingService
from trading_platform.core.services.new_market_state_machine_service import NewMarketStateMachineService
from trading_platform.exchanges.backtest import backtest_subclasses
from trading_platform.exchanges.data.financial_data import FinancialData
from trading_platform.exchanges.data.ticker import Ticker
from trading_platform.exchanges.exchange_service_abc import ExchangeServiceAbc
from trading_platform.storage.daos.open_order_dao import OpenOrderDao
from trading_platform.storage.daos.order_dao import OrderDao


class TestNewMarketStateMachineService(unittest.TestCase):
    def test(self):
        logger: logging.Logger = LoggingService.set_logger()
        exchanges_by_id: Dict[int, ExchangeServiceAbc] = backtest_subclasses.instantiate()
        open_order_dao: OpenOrderDao = OpenOrderDao()
        order_dao: OrderDao = OrderDao()
        sell_price: FinancialData = FinancialData(10)

        def random_sell_price(ticker: Ticker) -> FinancialData:
            return FinancialData(random.randint(5, 10))

        new_market_state_machine: NewMarketStateMachineService = NewMarketStateMachineService(logger=logger,
                                                                                exchanges_by_id=exchanges_by_id,
                                                                                open_order_dao=open_order_dao,
                                                                                order_dao=order_dao,
                                                                                sell_price=sell_price,
                                                                                sell_price_adjuster=random_sell_price)

        new_market_state_machine.next_state()
        eq_(new_market_state_machine.state['current_state'], 'buy')