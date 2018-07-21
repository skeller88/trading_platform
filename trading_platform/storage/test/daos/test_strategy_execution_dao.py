from nose.tools import eq_

from trading_platform.strategy.strategy_execution import StrategyExecution
from trading_platform.core.test.util_methods import eq_ignore_certain_fields
from trading_platform.exchanges.data.financial_data import FinancialData
from trading_platform.storage.daos.strategy_execution_dao import StrategyExecutionDao
from trading_platform.storage.test.daos.test_dao import TestDao


class TestStrategyExecutionDao(TestDao):
    __test__ = True  # important, makes sure tests are not run on base class
    dao_class = StrategyExecutionDao
    popo_class = StrategyExecution

    def setUp(self):
        self.dto1 = StrategyExecution(**{
            'strategy_id': 'ema_50_and_200_crossover',
            'state': {
                'base': 'BTC',
                'quote': 'XMR',
                'buy_order_id': '89y12hidsa781',
                'sell_price_stop': FinancialData(100),
                'sell_price_limit': FinancialData(70)
            }
        })
        self.dto2 = StrategyExecution(**{
            'strategy_id': 'bollinger_band',
            'state': {
                'base': 'BTC',
                'quote': 'NEO',
                'upper_band': FinancialData(150),
                'middle_band': FinancialData(140),
                'lower_band': FinancialData(130)
            }
        })

    def test_fetch_by_strategy_id(self):
        self.dao.bulk_save(session=self.session, commit=True, popos=[self.dto1, self.dto2])
        fetched = self.dao.fetch_by_column(session=self.session, column_name='strategy_id',
                                           column_value=self.dto1.strategy_id)
        eq_(len(fetched), 1)
        eq_ignore_certain_fields(fetched[0], self.dto1, ['db_id', 'db_create_timestamp'])

    def test_fetch_by_strategy_execution_id(self):
        self.dao.bulk_save(session=self.session, commit=True, popos=[self.dto1, self.dto2])
        fetched = self.dao.fetch_by_column(session=self.session, column_name='strategy_execution_id',
                                           column_value=self.dto1.strategy_execution_id)
        eq_(len(fetched), 1)
        eq_ignore_certain_fields(fetched[0], self.dto1, ['db_id', 'db_create_timestamp'])
