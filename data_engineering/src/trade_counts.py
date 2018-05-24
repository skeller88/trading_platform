import glob
import os
# from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import ThreadPoolExecutor

import pandas as pd
import regex

# from core.src.constants.arbitrage_pairs import arbitrage_pairs
from core.src.constants.arbitrage_pairs import arbitrage_pairs_list
from core.src.constants.paths import arbitrage_bot_src
from exchanges.src.data.enums import exchange_names
from exchanges.src.file_service import FileService

date_matcher = regex.compile('.*(20.*).csv.gz')


def trade_counts_by_min(df):
    df.index = pd.to_datetime(df.index, unit='ms')
    df = df.groupby(pd.TimeGrouper(freq='min')).count()
    df['trades_per_minute'] = df.id
    return df[['trades_per_minute']]


def trade_counts_for_file(exchange_name, pair, target_dir, filename):
    print('getting trade counts for file', filename)
    trade_df = pd.read_csv(filename, compression='gzip', index_col='date')
    trade_counts_df = trade_counts_by_min(trade_df)
    target_dir = os.path.join(target_dir, exchange_name, pair.kaiko_name)

    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    # Example: Binance_ADABTC_ticker_v2_2017_11_10.csv
    file_date = str(int(trade_counts_df.index.min().timestamp()))
    dest_fname = '{0}_{1}_trades_{2}.csv'.format(exchange_name, pair.kaiko_name, file_date)
    FileService.create_dirs_if_null([target_dir])
    dest_path = os.path.join(target_dir, dest_fname)
    print('writing to', dest_path)
    trade_counts_df.to_csv(dest_path)


def trade_count_group_by_minute(exchange_name, pair, source_dir, target_dir):
    """
    Group trades in each trade file by minute, and aggregate by count.
    Args:
        exchange_name:
        pair:
        source_dir:
        target_dir:

    Returns:

    """
    # Example: Binance_ADABTC_ob_10_2017_12_18.csv.gz
    glob_path = os.path.join(source_dir, exchange_name, pair.kaiko_name, '**',
                             '*{0}_trades*.csv.gz'.format(pair.kaiko_name))
    trade_files = glob.glob(glob_path, recursive=True)

    if len(trade_files) == 0:
        print('No data found for exchange {0} and pair {1}'.format(exchange_name, pair.kaiko_name))
        return

    with ThreadPoolExecutor(max_workers=25) as executor:
        for trade_file in trade_files:
            executor.submit(trade_counts_for_file, exchange_name, pair, target_dir, trade_file)


def trade_count_by_exchange_and_pair(exchange_name, pair, source_dir, target_dir):
    """
    Aggregate by exchange_name and pair.
    Args:
        exchange_name:
        pair:
        source_dir:
        target_dir:

    Returns:

    """
    target_dir = os.path.join(target_dir, exchange_name)
    FileService.create_dir_if_null(target_dir)
    glob_path = os.path.join(source_dir, exchange_name, pair.kaiko_name, '**',
                             '{0}_{1}_trades*.csv'.format(exchange_name, pair.kaiko_name))
    trade_files = glob.glob(glob_path, recursive=True)

    if len(trade_files) == 0:
        # print('No data found for exchange {0} and pair {1}'.format(exchange_name, pair.kaiko_name))
        return

    trades_df = FileService.load_and_concat_files(trade_files)
    trades_filename = '{0}_{1}_trades_agg.csv'.format(exchange_name, pair.kaiko_name)
    trades_df.to_csv(os.path.join(target_dir, trades_filename), index=False)


def trade_count_by_exchange(exchange_name, source_dir, target_dir):
    target_dir = os.path.join(target_dir, exchange_name)
    FileService.create_dir_if_null(target_dir)
    glob_path = os.path.join(source_dir, exchange_name, '**', '*trades*.csv'.format(exchange_name))
    trade_files = glob.glob(glob_path, recursive=True)

    if len(trade_files) == 0:
        # print('No data found for exchange {0} and pair {1}'.format(exchange_name, pair.kaiko_name))
        return

    def df_with_currency_column(trade_file):
        match = regex.search('{0}_(.*)_trades'.format(exchange_name), trade_file)
        try:
            trades_df = pd.read_csv(trade_file, index_col='date')
            trades_df['currency'] = match.group(1)
            return trades_df
        except Exception:
            return

    trade_df_for_exchange = pd.concat(filter(lambda x: x is not None, map(df_with_currency_column, trade_files)))
    trade_df_for_exchange_group_by_minute = pd.pivot_table(trade_df_for_exchange, index=['date'], columns='currency',
                                                           values=['trades_per_minute'])
    trade_df_for_exchange_group_by_minute = trade_df_for_exchange_group_by_minute.fillna(0)
    trades_filename = '{0}_trades_agg.csv'.format(exchange_name)
    trade_df_for_exchange_group_by_minute['trades_per_minute'].to_csv(os.path.join(target_dir, trades_filename))


derived_trades_dir = os.getcwd().replace(arbitrage_bot_src + '/data_engineering', 'kaiko/derived/trades')


def all_kaiko_data_trade_count_group_by_minute():
    source_dir = os.getcwd().replace(arbitrage_bot_src + '/data_engineering', 'kaiko/trades/zipped')
    target_dir = derived_trades_dir
    for exchange_name in [exchange_names.bittrex, exchange_names.binance, exchange_names.kraken]:
        for pair in arbitrage_pairs_list:
            trade_count_group_by_minute(exchange_name, pair, source_dir, target_dir)


def all_kaiko_data_trade_count_by_exchange_and_pair():
    source_dir = derived_trades_dir
    target_dir = os.getcwd().replace('core/data_engineering', 'data/kaiko/derived/trades')
    with ThreadPoolExecutor(max_workers=25) as executor:
        for exchange_name in [exchange_names.bittrex, exchange_names.binance, exchange_names.kraken]:
            for pair in arbitrage_pairs_list:
                executor.submit(trade_count_by_exchange_and_pair, exchange_name, pair, source_dir, target_dir)

def all_kaiko_data_trade_count_by_exchange():
    source_dir = os.getcwd().replace('core/data_engineering', 'data/kaiko/derived/trades')
    target_dir = os.getcwd().replace('core/data_engineering', 'data/kaiko/derived/trades')
    for exchange_name in [exchange_names.bittrex, exchange_names.binance, exchange_names.kraken]:
        trade_count_by_exchange(exchange_name, source_dir, target_dir)

# all_kaiko_data_trade_files_to_trade_counts()
# all_kaiko_data_trade_count_by_exchange_and_pair()
all_kaiko_data_trade_count_by_exchange()