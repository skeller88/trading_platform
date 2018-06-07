"""
Split ticker files containing tickers for all pairs and all exchanges into separate ticker files by pair and exchange.
"""
import glob
import os

import pandas

from trading_platform.core.services.file_service import FileService


class TickerEtlService:
    def __init__(self):
        self.file_service = FileService

    def by_exchange_and_pair(self, input_dir, output_dir):
        self.file_service.create_dir_if_null(output_dir)
        glob_path = os.path.join(input_dir, '**', '*ticker*.csv')
        ticker_files = glob.glob(glob_path, recursive=True)

        if len(ticker_files) == 0:
            # print('No data found for exchange {0} and pair {1}'.format(exchange_name, pair.kaiko_name))
            return

        for ticker_file in ticker_files:
            df = pandas.read_csv(ticker_file)
            df.processing_time = pandas.to_datetime(df.processing_time.astype(int), unit='s')
            group_columns = ['exchange_name', 'quote', 'base']
            g = df.groupby(group_columns).groups
            for gr, data in g.items():
                df_subset = df.iloc[data]
                file_date = str(int(df_subset.processing_time.min().timestamp()))
                pair_name = '{0}{1}'.format(gr[1], gr[2])
                group_dir = os.path.join(output_dir, gr[0], pair_name)
                self.file_service.create_dir_if_null(group_dir)
                target_filepath = os.path.join(group_dir, '{0}_{1}_ticker_v2_{2}.csv'.format(
                    gr[0], pair_name, file_date))
                print(target_filepath)
                df_subset.to_csv(target_filepath, index=False)

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
            columns = filter(lambda column: column not in ['processing_time', 'exchange_id'], df.columns)
            pt = df.pivot_table(index=pandas.Grouper(key='processing_time', freq=freq),
                                columns=['exchange_id'],
                                values=columns,
                                aggfunc=agg_func)

            # rearrange data in backtest ready schema
            resdf = pandas.DataFrame(index=pt.index)
            resdf['processing_time'] = pt.index
            return resdf



input_dir = os.getcwd().replace('core/data_engineering', 'data/arbitrage_finder/windows/ticker')
output_dir = os.getcwd().replace('core/data_engineering', 'data/arbitrage_finder/derived/ticker')

TickerEtlService.by_exchange_and_pair(input_dir, output_dir)