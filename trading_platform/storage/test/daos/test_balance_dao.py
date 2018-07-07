"""
nosetests test.storage.test_balance_dao --nocapture
"""

from trading_platform.core.test import data
from trading_platform.exchanges.data.balance import Balance
from trading_platform.exchanges.data.enums import exchange_ids
from trading_platform.storage.daos.balance_dao import BalanceDao
from trading_platform.storage.test.daos.test_dao import TestDao


class TestBalanceDao(TestDao):
    __test__ = True  # important, makes sure tests are not run on base class
    dao_class = BalanceDao
    popo_class = Balance

    def setUp(self):
        self.dto1 = data.balance(exchange_ids.binance)
        self.dto2 = data.balance(exchange_ids.bittrex)
