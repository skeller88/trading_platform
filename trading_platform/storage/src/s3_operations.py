import csv
import io
import os
from datetime import datetime

import smart_open

from trading_platform.exchanges.src.data.ticker import Ticker

LOCAL_DATA_DIR = "/Users/shanekeller/Documents/arbitrage_bot/data"


def write_tickers(write_to_s3, bucket='arbitrage-bot', tickers=[]):
    return write_result(write_to_s3, bucket, tickers, Ticker, Ticker.current_version)


def write_result(write_to_s3, bucket, results, result_class, file_version, filename_date_suffix=True):
    result_class_name = result_class.__name__.lower()
    date_suffix = '_{0}'.format(datetime.utcnow().strftime("%Y-%m-%dT%H:%M")) if filename_date_suffix else ''
    filename = '{0}_v{1}{2}.csv'.format(result_class_name, file_version, date_suffix)
    fieldnames = result_class.csv_fieldnames()
    if write_to_s3:
        filepath = '{0}/{1}/{2}'.format(bucket, result_class_name, filename)
        with smart_open.smart_open('s3://{0}'.format(filepath), 'wb') as fout:
            string_buffer = io.StringIO()
            writer = csv.DictWriter(string_buffer, fieldnames=fieldnames)
            writer.writeheader()
            fout.write(string_buffer.getvalue().encode('utf-8'))

            for result in results:
                string_buffer.seek(0)
                string_buffer.truncate(0)

                writer.writerow(result.to_dict())

                fout.write(string_buffer.getvalue().encode('utf-8'))
    else:
        local_dir = os.path.join(LOCAL_DATA_DIR, result_class_name)
        if not os.path.exists(local_dir):
            os.makedirs(local_dir)
        filepath = os.path.join(local_dir, filename)
        with open(filepath, 'w+') as history:
            writer = csv.DictWriter(history, fieldnames=fieldnames)
            writer.writeheader()

            for result in results:
                writer.writerow(result.to_dict())

    return filepath
