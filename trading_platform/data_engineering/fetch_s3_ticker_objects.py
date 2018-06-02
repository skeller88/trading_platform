"""
Before running this script, get access to the arbitrage-bot bucket.
"""
import datetime
import os

from trading_platform.aws_utils.s3_object_service import S3ObjectService

# V1+ fieldnames

def main(object_version, start_datetime, end_datetime):
    s3_object_service = S3ObjectService(object_version=object_version)
    output_dir = os.getcwd().replace('trading_platform/trading_platform/data_engineering', 'trading_data/tickers/debug')
    s3_object_service.window_objects(output_dir=output_dir, start_datetime=start_datetime,
                                     end_datetime=end_datetime, timedelta=datetime.timedelta(days=1),
                                     multithreading=True)

# main(object_version='4', start_datetime=datetime.datetime(2018, 3, 25), end_datetime=datetime.datetime(2018, 6, 1))
main(object_version='4', start_datetime=datetime.datetime(2018, 5, 29), end_datetime=datetime.datetime(2018, 6, 1))
# main(object_version='3', start_datetime=datetime.datetime(2018, 4, 7), end_datetime=datetime.datetime(2018, 4, 27))
# V1 and V2 data. See ticker_schema_version_changelog.md for details. The filename contains v0, incorrectly, but the
# version is 1 or 2. The script will correct that bug and write out the correct filename.
# main(object_version='0', start_datetime=datetime.datetime(2018, 1, 19), end_datetime=datetime.datetime(2018, 4, 7))
# main(object_version='3', start_datetime=datetime.datetime(2018, 4, 19), end_datetime=datetime.datetime(2018, 4, 27))