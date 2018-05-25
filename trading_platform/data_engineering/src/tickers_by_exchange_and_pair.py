"""
Split ticker files containing tickers for all pairs and all exchanges into separate ticker files by pair and exchange.
"""
import glob
import os

import pandas

from trading_platform.exchanges.src.file_service import FileService


def main(source_dir, target_dir):
    FileService.create_dir_if_null(target_dir)
    glob_path = os.path.join(source_dir, '**', '*ticker*.csv')
    trade_files = glob.glob(glob_path, recursive=True)

    if len(trade_files) == 0:
        # print('No data found for exchange {0} and pair {1}'.format(exchange_name, pair.kaiko_name))
        return

    for trade_file in trade_files:
        df = pandas.read_csv(trade_file)
        df.processing_time = pandas.to_datetime(df.processing_time.astype(int), unit='s')
        group_columns = ['exchange_name', 'quote', 'base']
        g = df.groupby(group_columns).groups
        for gr, data in g.items():
            df_subset = df.iloc[data]
            file_date = str(int(df_subset.processing_time.min().timestamp()))
            pair_name = '{0}{1}'.format(gr[1], gr[2])
            group_dir = os.path.join(target_dir, gr[0], pair_name)
            FileService.create_dir_if_null(group_dir)
            target_filepath = os.path.join(group_dir, '{0}_{1}_ticker_v2_{2}.csv'.format(
                gr[0], pair_name, file_date))
            print(target_filepath)
            df_subset.to_csv(target_filepath, index=False)

source_dir = os.getcwd().replace('core/data_engineering', 'data/arbitrage_finder/windows/ticker')
target_dir = os.getcwd().replace('core/data_engineering', 'data/arbitrage_finder/derived/ticker')

main(source_dir, target_dir)