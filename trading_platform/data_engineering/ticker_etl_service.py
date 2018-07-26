"""
Split ticker files containing tickers for all pairs and all exchanges into separate ticker files by pair and exchange.
"""
import time

import glob
import ntpath
import os
import pandas
import random
from typing import List, Callable, Optional

from trading_platform.core.services.file_service import FileService
from trading_platform.exchanges.data.enums import exchange_ids


class TickerEtlService:
    # Version of standardized ticker files
    standard_version: int = 0

    def __init__(self, file_service: FileService):
        self.file_service = file_service

    def run_pipeline(self, input_dir, output_dir, pipeline: List[Callable[[pandas.DataFrame], Optional[pandas.DataFrame]]]):
        self.file_service.create_dir_if_null(output_dir)
        glob_path: str = os.path.join(input_dir, '**', '*ticker*.csv')

        ticker_filenames: List[str] = glob.glob(glob_path, recursive=True)
        files_processed: int = 0
        start_time = time.time()
        for ticker_filename in ticker_filenames:
            files_processed += 1
            if random.randint(0, 1000) == 0:
                print('{0} files processed in {1} seconds'.format(files_processed, (time.time() - start_time)))

            ticker_df = TickerEtlService.read_csv(ticker_filename, False)

            for method in pipeline:
                if ticker_df is None:
                    break
                ticker_df = method(ticker_df)

            if ticker_df is not None:
                basename:str = ntpath.basename(ticker_filename)
                ticker_df.to_csv(os.path.join(output_dir, basename), sep=',', mode='w+')

    @staticmethod
    def standardize(ticker_df: pandas.DataFrame) -> Optional[pandas.DataFrame]:
        # Ignore this version of files because they don't include the bid and ask fields.
        if any(ticker_df['version'] == 0):
            return

        # backwards compatibility. "exchange_name" is a column in Ticker data v2 and lower, and "exchange_id" is a
        # column for Ticker data v3 and higher. See docs/ticker_schema_version_changelog.md for a detailed explanation
        # of schema changes.
        if ticker_df.version.iloc[0] < 3:
            colname = 'exchange_id' if ticker_df.version.iloc[0] == 2 else 'exchange_name'
            ticker_df['exchange_id'] = ticker_df[colname].apply(lambda x: exchange_ids.from_name(x))

            if ticker_df.version.iloc[0] < 2:
                ticker_df.drop('exchange_name', axis=1)

        if 'processing_time' in ticker_df.columns:
            ticker_df.rename(columns={'processing_time': 'app_create_timestamp'}, inplace=True)

        ticker_df['standard_version'] = 0

        return ticker_df

    def by_exchange_and_pair(self, input_dir, output_dir):
        self.file_service.create_dir_if_null(output_dir)
        glob_path = os.path.join(input_dir, '**', '*ticker*.csv')
        ticker_files = glob.glob(glob_path, recursive=True)

        if len(ticker_files) == 0:
            # print('No data found for exchange {0} and pair {1}'.format(exchange_name, pair.kaiko_name))
            return

        for ticker_file in ticker_files:
            print(ticker_file)
            df = pandas.read_csv(ticker_file)

            app_create_timestamp_col_name = 'app_create_timestamp' if 'app_create_timestamp' in df.columns else 'processing_time'
            df['app_create_timestamp'] = pandas.to_datetime(df[app_create_timestamp_col_name].astype(int), unit='s')

            # backwards compatibility. "exchange_name" is a column in Ticker data v2 and lower, and "exchange_id" is a
            # column for Ticker data v3 and higher. See docs/ticker_schema_version_changelog.md for a detailed explanation
            # of schema changes.
            if 'exchange_name' in df.columns:
                df['exchange_id'] = df['exchange_name'].apply(lambda x: exchange_ids.from_name(x))

            version = df['version'].iloc[0]
            group_columns = ['exchange_id', 'quote', 'base']
            g = df.groupby(group_columns).groups
            try:
                for gr, data in g.items():
                    exchange_id_str: str = str(gr[0])
                    quote: str = gr[1]
                    base: str = gr[2]
                    df_subset = df.iloc[data]
                    file_date = str(int(df_subset.app_create_timestamp.min().timestamp()))
                    pair_name = '{0}{1}'.format(quote, base)
                    group_dir = os.path.join(output_dir, exchange_id_str, pair_name)
                    self.file_service.create_dir_if_null(group_dir)
                    target_filepath = os.path.join(group_dir, '{0}_{1}_ticker_v{2}_{3}.csv'.format(
                        exchange_id_str, pair_name, version, file_date))
                    df_subset.to_csv(target_filepath, index=False, mode='w+')
            except Exception:
                print('foo')

    def aggregate(self, input_dir, output_dir, windows_per_file=3300):
        """
        Aggregate ticker files and write to csv.

        Each ticker file is about 150KB. 0.5 GB is a safe amount of memory per file.
        0.5 GB * 1000MB/GB * 1000KB/MB * 1/150KB = 3333 files.
        """
        self.file_service.create_dir_if_null(output_dir)
        glob_path = os.path.join(input_dir, '**', '*ticker*.csv')
        ticker_filenames: List[str] = glob.glob(glob_path, recursive=True)
        ticker_filenames.sort()

        windows_added: int = 0
        ticker_dfs: List[pandas.DataFrame] = []

        for ticker_filename in ticker_filenames:
            if windows_added < windows_per_file:
                ticker_df = FileService.read_csv(ticker_filename, True)
                if ticker_df is not None:
                    ticker_dfs.append(ticker_df)
                windows_added += 1
            else:
                if len(ticker_dfs) > 0:
                    agg_ticker_df: pandas.DataFrame = pandas.concat(ticker_dfs)
                    agg_ticker_df.sort_values(by='app_create_timestamp', inplace=True)
                    earliest_window: str = str(agg_ticker_df.iloc[0]['app_create_timestamp'])
                    filename: str = 'ticker_agg_{0}'.format(earliest_window)
                    print('aggregated tickers in file {0}'.format(filename))
                    agg_ticker_df.to_csv(os.path.join(output_dir, filename))

                windows_added = 0
                ticker_dfs = []
