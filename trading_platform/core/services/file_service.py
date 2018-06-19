"""
Used for file-related operations such as finding csv files for exchanges, concatenating csv files into a dataframe,
and grouping csv files by time.

Also performs other file operations such as creating parent directories for a new directory.
"""
import csv
import datetime
import re

import os
from typing import Generator

import pandas as pd
from setuptools import glob

from trading_platform.exchanges.data.pair import Pair
from trading_platform.exchanges.data.ticker import Ticker
from trading_platform.utils.exceptions import DuplicateDataException


class FileService:
    @staticmethod
    def create_dirs_if_null(dir_names):
        [FileService.create_dir_if_null(dir_name) for dir_name in dir_names]


    @staticmethod
    def create_dir_if_null(dir_name):
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)

    @staticmethod
    def load_and_concat_files(csv_filenames):
        dfs = [pd.read_csv(csv_filename) for csv_filename in csv_filenames]

        if len(dfs) == 0:
            return
        df = pd.concat(dfs)
        return df

    @staticmethod
    def csv_filenames_for_exchange_names_and_pair_name(exchange_names, pair_name, source_dir):
        """
        Fetch csv files that contain data for the given pair_name for any of the exchanges in exchange_names. Example,
        '<source_dir>/Binance/Binance_ADABTC_ticker_v2_2017_11_10.csv'
        Args:
            exchange_names:
            pair_name:
            source_dir:

        Returns list(str): filenames matching the glob patterns for the exchange names and pair name

        """
        filenames = []
        for exchange_name in exchange_names:
            # Example: ,
            glob_pattern = os.path.join(source_dir, exchange_name, pair_name, '{0}_{1}*.csv'.format(exchange_name, pair_name))
            filenames.extend(glob.glob(glob_pattern))

        return filenames

    @staticmethod
    def csv_filename_generator(start_timestamp, end_timestamp, csv_operation_config):
        """
        :param start_timestamp: fetch tickers >= this utc timestamp
        :param end_timestamp: fetch tickers < this utc timestamp
        :param csv_operation_config: metadata about where the ticker data is located and how to retrieve it. Is this
        in a csv file, a database?
        :return:
        """
        source_filepath = csv_operation_config.source_filepath
        date_string_pattern = '(.*){0}(.*).csv'.format(csv_operation_config.source_prefix)
        date_string_regex = re.compile(date_string_pattern)

        for csv_filename in glob.glob('{0}/*.csv'.format(source_filepath)):
            date_string_regex_match = date_string_regex.match(csv_filename)
            if date_string_regex_match is not None and len(date_string_regex_match.groups()) == 2:
                # The API around .groups() is confusing. The total number of groups accessible via .group() is always
                # == len(.groups()) + 1.
                date_string = date_string_regex_match.group(2)
                file_datetime = pd.Timestamp(date_string)
                file_timestamp = file_datetime.timestamp()

                if start_timestamp <= file_timestamp < end_timestamp:
                    yield csv_filename

    @staticmethod
    def datetime_generator(start_datetime: datetime.datetime, end_datetime: datetime.datetime,
                           timedelta: datetime.timedelta) -> Generator[datetime.datetime, None, None]:
        """
        Generate datetimes within a range >= start_datetime and < end_datetime
        """
        next_datetime = start_datetime
        while next_datetime < end_datetime:
            yield next_datetime
            next_datetime = next_datetime + timedelta


    @staticmethod
    def fetch_tickers(exchange_id, start_timestamp, end_timestamp, data_operation_config, distinct=True):
        """
        TODO - This method is currently unused. Decide whether to keep it.
        :param start_timestamp: fetch tickers >= this utc timestamp
        :param end_timestamp: fetch tickers < this utc timestamp
        :param data_operation_config: metadata about where the ticker data is located and how to retrieve it. Is this
        in a csv file, a database?
        :param group_by_time:
        :return:
        """
        file_gen = FileService.csv_filename_generator(start_timestamp, end_timestamp, data_operation_config)
        tickers = {}
        for csv_filename in file_gen:
            with open(csv_filename, 'r') as fileobj:
                reader = csv.DictReader(fileobj)
                for row in reader:
                    ticker = Ticker.from_csv_data(row, 0)

                    # Only ticker versions 1 and up have ask and bid data
                    if ticker.version < 1:
                        print('.', end='')
                        continue

                    if ticker.exchange_id != exchange_id:
                        print(',', end='')
                        continue
                    pair_name = Pair(base=ticker.base, quote=ticker.quote).name
                    # Need to address the issue that exchange data is not in UTC :/.
                    #                             exchange_timestamp = ticker.exchange_timestamp / 1000
                    exchange_timestamp = ticker.app_create_timestamp
                    if not start_timestamp <= exchange_timestamp < end_timestamp:
                        print('#', end='')
                        continue

                    if distinct and tickers.get(pair_name) is not None:
                        raise Exception('Ticker with pair_name {0} already exists. Choose a narrower range.'.format(
                            pair_name))

                    tickers[pair_name] = ticker
        return tickers if len(tickers) > 0 else None

    # Methods used in

    @staticmethod
    def group_by_time(tdf, ticker_freq):
        ftdf = tdf[(tdf['version'] > 0) &
                   (tdf['version'] <= 2) &
                   (tdf['base'] != '456')] \
            .drop_duplicates().copy()

        ftdf['pd_datetime'] = pd.to_datetime((ftdf['app_create_timestamp'] * 1e9) \
                                             .astype(int), unit='ns')

        c = ftdf.groupby([pd.Grouper(key='pd_datetime', freq=ticker_freq),
                          'base', 'quote', 'exchange_id'])['bid', 'ask'].count()

        if len(c['bid'].value_counts()) > 1:
            raise DuplicateDataException()

        pvt_index = [pd.Grouper(key='pd_datetime', freq=ticker_freq), 'base', 'quote']
        pvt = ftdf.pivot_table(index=pvt_index,
                               columns=['exchange_name'],
                               values=['bid', 'ask'],
                               aggfunc='min')
        return pvt
