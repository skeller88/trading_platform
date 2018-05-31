import math
import os
import unittest
from copy import deepcopy

import pandas
from nose.tools import eq_
from s3fs import S3FileSystem

from database_snapshot.src import snapshot
from arbitrage_executer.src.market_data.arbitrage_attempt import ArbitrageAttempt
from trading_platform.exchanges.data.enums import exchange_ids
from trading_platform.exchanges.data.order import Order
from trading_platform.exchanges.data.utils import check_required_fields
from arbitrage_executer.src.daos.arbitrage_attempt_dao import ArbitrageAttemptDao
from trading_platform.storage.daos.order_dao import OrderDao
from trading_platform.storage.sql_alchemy_engine import SqlAlchemyEngine
from trading_platform.core.test import data


class TestSnapshot(unittest.TestCase):
    def setUp(self):
        self.engine = SqlAlchemyEngine.local_engine_maker()
        self.engine.initialize_tables()
        self.session = self.engine.scoped_session_maker()
        self.arbitrage_attempt_dao = ArbitrageAttemptDao()
        self.order_dao = OrderDao()

        timestamp_delta = 50000.
        # Orders for arbitrage attempt 1
        self.low1_1 = data.order(exchange_ids.binance)
        # simulate storage of multiple snapshots of the same order
        self.low1_2 = deepcopy(self.low1_1)
        self.low1_2.processing_time = self.low1_2.processing_time + timestamp_delta
        self.high1_1 = data.order(exchange_ids.bittrex)
        self.high1_2 = deepcopy(self.high1_1)
        self.high1_2.processing_time = self.high1_2.processing_time + timestamp_delta

        # Orders for arbitrage attempt 2
        self.low2_1 = data.order(exchange_ids.binance)
        self.high2_1 = data.order(exchange_ids.bittrex)

        self.orders = [self.low1_1, self.low1_2, self.high1_1, self.high1_2, self.low2_1, self.high2_1]
        self.order_dao.bulk_save(self.session, commit=True, popos=self.orders)

        aa1 = data.arbitrage_attempt(high_order_index=self.low1_1.order_index,
                                     low_order_index=self.high1_1.order_index)
        aa2 = data.arbitrage_attempt(high_order_index=self.low2_1.order_index,
                                     low_order_index=self.high2_1.order_index)
        self.aas = [aa1, aa2]
        self.arbitrage_attempt_dao.bulk_save(self.session, commit=True, popos=self.aas)

    def tearDown(self):
        self.arbitrage_attempt_dao.delete_all(session=self.session)
        self.order_dao.delete_all(session=self.session)
        self.session.commit()
        self.session.close_all()

        self.engine.drop_tables()

    def test_csv_format_local(self):
        """
        Database snapshots for arbitrage attempts and orders should be written to csv files in the expected formats.

        To simulate AWS functionality, run:
        export ENV=prod && nosetests database_snapshots.test.arbitrage_attempts_and_orders.test_lambda_handler:TestLambdaHandler.test_csv_format

        """
        start_processing_time = -math.inf
        snapshot_filepaths = snapshot.main(write_to_s3=False, arbitrage_attempt_dao=self.arbitrage_attempt_dao,
                                           order_dao=self.order_dao, session=self.session,
                                           start_processing_time=start_processing_time)

        aa_df = pandas.read_csv(snapshot_filepaths['arbitrage_attempts_filepath'])
        order_df = pandas.read_csv(snapshot_filepaths['order_filepath'], dtype={
            field: pandas.np.float64 for field in Order.financial_data_fields()
        }, index_col='order_index')

        self.check_df_contents(aa_df, order_df)

        # cleanup
        os.remove(snapshot_filepaths['arbitrage_attempts_filepath'])
        os.remove(snapshot_filepaths['order_filepath'])

    def test_csv_format_remote(self):
        """
        Database snapshots for arbitrage attempts and orders should be written to csv files in the expected formats.

        To simulate AWS functionality, run:
        export ENV=prod && nosetests database_snapshots.test.arbitrage_attempts_and_orders.test_lambda_handler:TestLambdaHandler.test_csv_format

        """
        start_processing_time = -math.inf
        snapshot_filepaths = snapshot.main(write_to_s3=True, arbitrage_attempt_dao=self.arbitrage_attempt_dao,
                                           order_dao=self.order_dao, session=self.session,
                                           start_processing_time=start_processing_time)

        s3 = S3FileSystem(anon=False)
        aa_df = pandas.read_csv(s3.open(snapshot_filepaths['arbitrage_attempts_filepath']))
        order_df = pandas.read_csv(s3.open(snapshot_filepaths['order_filepath']), dtype={
            field: pandas.np.float64 for field in Order.financial_data_fields()
        }, index_col='order_index')

        self.check_df_contents(aa_df, order_df)

        # cleanup
        s3 = S3FileSystem(anon=False)
        s3.rm(snapshot_filepaths['arbitrage_attempts_filepath'])
        s3.rm(snapshot_filepaths['order_filepath'])

    def check_df_contents(self, aa_df, order_df):
        # Test arbitrage attempt response
        eq_(len(aa_df), len(self.aas))
        eq_(len(aa_df.columns), len(ArbitrageAttempt.csv_fieldnames()))
        aa_series = aa_df.iloc[0]
        aa = ArbitrageAttempt(**aa_series.to_dict())
        check_required_fields(aa)

        # Test order response
        eq_(len(order_df), len(self.orders))
        # minus 1 because order_index is the index_col
        num_cols = len(Order.csv_fieldnames()) - 1
        eq_(len(order_df.columns), num_cols)
        # There should be multiple orders for certain order indexes
        eq_(len(order_df.loc[self.low1_1.order_index]), 2)
        eq_(len(order_df.loc[self.high1_1.order_index]), 2)
        # But not others. Since only one series is returned, the series fields are returned, rather
        # than an array of series
        eq_(len(order_df.loc[self.low2_1.order_index]), num_cols)
        eq_(len(order_df.loc[self.high2_1.order_index]), num_cols)
        order_series = order_df.iloc[0]
        order = Order(**order_series.to_dict())
        check_required_fields(order)