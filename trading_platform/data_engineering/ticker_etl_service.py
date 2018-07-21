"""
Split ticker files containing tickers for all pairs and all exchanges into separate ticker files by pair and exchange.
"""
import glob
import os

import pandas

from trading_platform.core.services.file_service import FileService
from trading_platform.exchanges.data.enums import exchange_ids


class TickerEtlService:
    def __init__(self, file_service: FileService):
        self.file_service = file_service

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

    def group_by_freq(self, input_dir, output_dir, agg_func, freq='min'):
        """
        Group by frequency

        Args:
            input_dir:
            output_dir:
            agg_func:
            freq:

        Returns:

        """
        self.file_service.create_dir_if_null(output_dir)
        glob_path = os.path.join(input_dir, '**', '*ticker*.csv')
        ticker_files = glob.glob(glob_path, recursive=True)

        def run(df):
            # TODO: this aggregates blindly assuming only 1 pair, if multiple pairs this needs to change
            columns = filter(lambda column: column not in ['app_create_timestamp', 'exchange_id'], df.columns)
            pt = df.pivot_table(index=pandas.Grouper(key='app_create_timestamp', freq=freq),
                                columns=['exchange_id'],
                                values=columns,
                                aggfunc=agg_func)

            # rearrange data in backtest ready schema
            resdf = pandas.DataFrame(index=pt.index)
            resdf['app_create_timestamp'] = pt.index
            return resdf
