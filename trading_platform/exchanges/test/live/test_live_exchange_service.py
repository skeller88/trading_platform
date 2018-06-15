"""
Test exchange live functionality.

Exchanges won't allow for multiple accounts per exchange. So, the same exchange has to be used for trading
and testing. This creates some trickiness, for example, when asserting the number of open orders is as expected,
the number of open orders could vary depending on which production orders were placed.
"""
import unittest
from time import sleep

import pandas
from nose.tools import eq_, assert_true, assert_greater

from trading_platform.core.test.data import Defaults
from trading_platform.exchanges.data.enums import exchange_ids
from trading_platform.exchanges.data.financial_data import zero
from trading_platform.exchanges.data.pair import Pair
from trading_platform.exchanges.data.utils import check_required_fields
from trading_platform.exchanges.live.binance_live_service import BinanceLiveService
from trading_platform.exchanges.live.live_subclasses import exchange_service_credentials_for_exchange, \
    test_exchange_credentials_param, exchange_credentials_param
from trading_platform.storage.daos.balance_dao import BalanceDao
from trading_platform.storage.sql_alchemy_engine import SqlAlchemyEngine


class TestLiveExchangeService(unittest.TestCase):
    __test__ = True  # important, makes sure tests are not run on base class
    # Each inheritor of this class will set these values
    live_service_class = BinanceLiveService
    xrp_tag_len = None

    @classmethod
    def setUpClass(cls):
        cls.pair = Pair(base='USDT', quote='ETH')
        cls.engine = SqlAlchemyEngine.local_engine_maker()
        cls.engine.initialize_tables()
        cls.session = cls.engine.scoped_session_maker()
        cls.balance_dao = BalanceDao()
        # credentials = exchange_service_credentials_for_exchange(cls.live_service_class, param_name=test_exchange_credentials_param)
        credentials = exchange_service_credentials_for_exchange(cls.live_service_class, param_name=exchange_credentials_param)
        withdrawal_fees = pandas.DataFrame(
            {'currency': cls.pair.base, 'withdrawal_fee': Defaults.base_withdrawal_fee},
            {'currency': cls.pair.quote, 'withdrawal_fee': Defaults.quote_withdrawal_fee}
        )
        cls.service = cls.live_service_class(credentials.get('key'), credentials.get('secret'),
                                             withdrawal_fees=withdrawal_fees)
        # Bittrex in particular has slow consistency and takes a second or more for changes to be persisted.
        cls.sleep_sec_consistency = 4

    def setUp(self):
        """
        Avoid rate limiting.
        Returns:

        """
        sleep(5)

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
        eq_(deposit_destination.tag, None)

    def test_fetch_deposit_destination_with_tag(self):
        deposit_destination = self.service.fetch_deposit_destination('XRP', {})
        eq_(len(deposit_destination.address), 34)
        eq_(deposit_destination.status, 'ok')
        eq_(len(deposit_destination.tag), self.xrp_tag_len)

    def test_fetch_balances(self):
        eq_(self.service.get_balance(self.pair.base), zero)
        self.service.fetch_balances()
        base_balance = self.service.get_balance(self.pair.base)
        assert_true(base_balance)
        assert_greater(base_balance, zero)

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

    @staticmethod
    def fetch_open_orders_for_order_instances(exchange_service, order_instances):
        """

        Args:
            order_instances list(Order):

        Returns:

        """
        open_orders = {}

        for order in order_instances:
            open_orders.update(exchange_service.fetch_open_orders(Pair(base=order.base, quote=order.quote).name_for_exchange_clients))

        return open_orders
