from nose.tools import eq_

from trading_platform.strategy.strategy import Strategy
from trading_platform.core.test.util_methods import eq_ignore_certain_fields
from trading_platform.storage.daos.strategy_dao import StrategyDao
from trading_platform.storage.test.daos.test_dao import TestDao


class TestStrategyDao(TestDao):
    __test__ = True  # important, makes sure tests are not run on base class
    dao_class = StrategyDao
    popo_class = Strategy

    def setUp(self):
        self.dto1 = Strategy(**{
            'strategy_id': 'ema_50_and_200_crossover',
            'properties': {
                'period': 'day',
                'leading_ema': 50,
                'lagging_ema': 200
            }
        })
        self.dto2 = Strategy(**{
            'strategy_id': 'bollinger_band_21_day',
            'properties': {
                'moving_average_length': 21,
                'moving_average_period': 'day',
            }
        })

    def test_fetch_by_strategy_id(self):
        self.dao.bulk_save(session=self.session, commit=True, popos=[self.dto1, self.dto2])

        fetched = self.dao.fetch_by_column(session=self.session, column_name='strategy_id',
                                           column_value=self.dto1.strategy_id)
        eq_(len(fetched), 1)
        eq_ignore_certain_fields(fetched[0], self.dto1, ['db_id', 'db_create_timestamp'])
