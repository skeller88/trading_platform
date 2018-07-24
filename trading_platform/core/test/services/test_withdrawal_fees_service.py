import pandas

import os

import unittest
from nose.tools import assert_false
from typing import Dict

from trading_platform.exchanges.data.enums import exchange_ids
from trading_platform.exchanges.withdrawal_fees_service import WithdrawalFeesService


class TestWithdrawalFeesService(unittest.TestCase):
    def setUp(self):
        self.withdrawal_fees_dir = os.path.dirname(__file__).replace('core/test/services', 'withdrawal_fees')

    def test_get_by_exchange_ids(self):
        fees_by_exchange_ids: Dict[int, pandas.DataFrame] = WithdrawalFeesService.get_by_exchange_ids()
        for exchange_id in exchange_ids.all_ids:
            if exchange_id in [exchange_ids.binance, exchange_ids.bittrex, exchange_ids.poloniex, exchange_ids.kraken,
                               exchange_ids.kucoin, exchange_ids.coinbase]:
                assert (fees_by_exchange_ids[exchange_id].at['ETH', 'withdrawal_fee'] is not None)
            else:
                assert_false('ETH' in fees_by_exchange_ids[exchange_id].index)
