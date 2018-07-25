"""
Split ticker files containing tickers for all pairs and all exchanges into separate ticker files by pair and exchange.
"""
import glob
import os

import pandas
from typing import List, Callable, Optional

from trading_platform.core.services.file_service import FileService
from trading_platform.exchanges.data.enums import exchange_ids


class TickerEtlService:
    # Version of standardized ticker files
    standard_version: int = 0

    def __init__(self, file_service: FileService):
        self.file_service = file_service

    def run_pipeline(self, input_dir, output_dir, pipeline: List[Callable[[str], Optional[pandas.DataFrame]]]):
        self.file_service.create_dir_if_null(output_dir)
        glob_path: str = os.path.join(input_dir, '**', '*ticker*.csv')

        ticker_files: List[str] = glob.glob(glob_path, recursive=True)
        for ticker_file in ticker_files:
            for method in pipeline:
                ticker_file = method(ticker_file)

            ticker_file.to_csv(os.path.join(output_dir), 'w+')

    def standardize(self, ticker_file: str) -> Optional[pandas.DataFrame]:
        ticker_df: pandas.DataFrame = pandas.read_csv(ticker_file)

        # Ignore this version of files because they don't include the bid and ask fields.
        if any(ticker_df['version'] == 0):
            return

        # backwards compatibility. "exchange_name" is a column in Ticker data v2 and lower, and "exchange_id" is a
        # column for Ticker data v3 and higher. See docs/ticker_schema_version_changelog.md for a detailed explanation
        # of schema changes.
        if 'exchange_name' in ticker_df.columns:
            ticker_df['exchange_id'] = ticker_df['exchange_name'].apply(lambda x: exchange_ids.from_name(x))

        ticker_df['app_create_timestamp'] = ticker_df[
            'app_create_timestamp'] if 'app_create_timestamp' in ticker_df.columns else ticker_df['processing_time']

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

    def group_by_freq(self, input_dir, output_dir, windows_per_file: 60, freq='min'):
        """
        Group ticker files by frequency and write to csv.
        """
        self.file_service.create_dir_if_null(output_dir)
        glob_path = os.path.join(input_dir, '**', '*ticker*.csv')
        ticker_files = glob.glob(glob_path, recursive=True)

        windows_added: int = 0

        for ticker_file in ticker_files:
            ticker_dfs: List[pandas.DataFrame] = []
            while windows_added < windows_per_file:
                ticker_df = pandas.read_csv(ticker_file)
                ticker_dfs.append(ticker_df)
                windows_added += 1
            ticker_agg_df: pandas.DataFrame = pandas.concat(ticker_dfs)
            ticker_agg_df.groupby(pandas.Grouper(key='app_create_timestamp', freq=freq))
            earliest_window: str = '0'

            ticker_agg_df.to_csv(os.path.join(output_dir, 'ticker_agg_{0}'.format(earliest_window)))
