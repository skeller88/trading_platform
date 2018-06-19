import glob
import os
# from concurrent.futures import ThreadPoolExecutor
import traceback
from concurrent.futures import ThreadPoolExecutor

import numpy as np
import pandas as pd
import regex

# from core.src.constants.arbitrage_pairs import arbitrage_pairs
from trading_platform.core.constants.currency_pairs import currency_pairs_list
from trading_platform.core.services.file_service import FileService
from trading_platform.exchanges.data.enums import exchange_names

date_matcher = regex.compile('.*(20.*).csv.gz')


def bid_ask_df_from_ob_file(fpath):
    fname = os.path.split(fpath)[1]
    df = pd.read_csv(fpath, compression='gzip')

    #table indexed by date with 4 columns:
    # (min, a), (max, a), (min, b), (max, b)
    pvt = df.pivot_table(index='date', columns='type',
                         values='price', aggfunc=(min, max))

    n_rows = len(pvt)
    n_missing = np.count_nonzero(pvt.isnull().values.any(axis=1))

    if n_missing > 0:
        perc = n_missing / n_rows * 100.0
        print("{}: rows: {}, missing rows: {}. {:0.3f}%. Dropping them.".format(fname, n_rows, n_missing, perc))
        pvt = pvt.dropna()

    # this checks if 'a' and 'b' roles are inverted
    if (pvt[('min', 'a')] <= pvt[('max', 'b')]).all():
        res = pvt[[('max', 'a'), ('min', 'b')]].reset_index()
    elif (pvt[('min', 'b')] <= pvt[('max', 'a')]).all():
        res = pvt[[('max', 'b'), ('min', 'a')]].reset_index()
    else:
        raise Exception("Data does not make sense. Please check it.")

    res.columns = ['exchange_timestamp', 'bid', 'ask']

    check = res['bid'] > res['ask']
    if check.any():
        n_wrong = len(check[check])
        n_rows = len(check)
        perc = n_wrong / n_rows * 100.0
        print("{}: rows: {}, rows with crossed spread: {}. {:0.3f}%. Dropping them".format(fname, n_rows, n_wrong, perc))
        res = res[~check]
    assert ((res['bid'] <= res['ask']).all())
    return res


def main(exchange_name, pair, source_filepath, target_filepath):
    # Example: Binance_ADABTC_ob_10_2017_12_18.csv.gz
    glob_path = os.path.join(source_filepath, exchange_name, pair.kaiko_name, '**', '*{0}*.csv.gz'.format(pair.kaiko_name))
    files = glob.glob(glob_path, recursive=True)
    files.sort()

    if len(files) == 0:
        # print('No data found for exchange {0} and pair {1}'.format(exchange_name, pair))
        return

    # print('order_book data to tickers for exchange {0} and pair {1}'.format(exchange_name, pair))

    target_filepath = os.path.join(target_filepath, exchange_name, pair.kaiko_name)
    if not os.path.exists(target_filepath):
        os.makedirs(target_filepath)

    # Example: Binance_ADABTC_ticker_v2_2017_11_10.csv
    for gzip_filename in files:
        try:
            orders = bid_ask_df_from_ob_file(gzip_filename)
        except Exception:
            print('Exception during bid_ask_df_from_ob_file', gzip_filename)
            traceback.print_exc()

        # complete the schema
        orders['base'] = pair.base
        orders['quote'] = pair.quote
        orders['exchange_name'] = exchange_name
        orders['app_create_timestamp'] = orders['exchange_timestamp']
        orders['version'] = 2

        file_date = str(pd.to_datetime(orders['exchange_timestamp'].values.min(), unit='ms').date())
        dest_fname = '{0}_{1}_ticker_v2_{2}.csv'.format(exchange_name, pair.kaiko_name, file_date)
        dest_path = os.path.join(target_filepath, pair.kaiko_name, dest_fname)
        FileService.create_dirs_if_null([dest_path])
        # write to file
        orders[['ask', 'bid', 'base', 'exchange_name',
                'exchange_timestamp', 'quote',
                'app_create_timestamp', 'version']].to_csv(dest_path, index=False)

    print('Success: order_book data to tickers for exchange {0} and pair {1}'.format(exchange_name, pair))

def test():
    source_filepath = './data/kaiko/order_books'
    target_filepath = './data/kaiko/derived/tickers'
    with ThreadPoolExecutor(max_workers=25) as executor:
        for exchange in [exchange_names.bittrex, exchange_names.binance, exchange_names.kraken]:
            for pair in currency_pairs_list:
                executor.submit(main, exchange, pair, source_filepath, target_filepath)

def all_kaiko_data():
    source_filepath = '../kaiko_data/order_books/unzipped'
    target_filepath = '../kaiko/derived/tickers'
    with ThreadPoolExecutor(max_workers=25) as executor:
        for exchange in [exchange_names.bittrex, exchange_names.binance, exchange_names.kraken]:
            for pair in currency_pairs_list:
                executor.submit(main, exchange, pair, source_filepath, target_filepath)

all_kaiko_data()
# test()