"""
Before running this script, get access to the arbitrage-bot bucket.
"""
from concurrent.futures import ThreadPoolExecutor


# V0 fieldnames
# fieldnames = [
#     'time',
#     'pair',
#     'high_exchange',
#     'high_price',
#     'low_exchange',
#     'low_price',
#     'percent_profit',
#     'spread'
# ]

# V1+ fieldnames
from analytics.src.s3_objects_fetcher import S3ObjectFetcher


def get_and_write_data_with_prefix(timedelta_days, timedelta_hours, object_version, fieldnames):
    s3of = S3ObjectFetcher(object_type='ticker',
                           record_version=object_version,
                           fieldnames=fieldnames
                           )
    # time_filter = '%Y-%m-%dT%H:%m'
    time_filter = '%Y-%m-%d'
    output_file, prefix = s3of.get_output_file(timedelta_days=timedelta_days,
                                               timedelta_hours=timedelta_hours, time_filter=time_filter)
    lines = s3of.get_data(prefix)
    s3of.write_data(output_file, lines)


def fetch_s3_ticker_objects(start_timedelta_days, end_timedelta_days, object_version, fieldnames, multithreading=True):
    """
    Args:
        start_timedelta_days: earliest date, 0 for today
        end_timedelta_days: latest date, example, 30 for a month ago
        object_version:
        fieldnames:

    Returns:

    """
    if multithreading:
        with ThreadPoolExecutor(max_workers=20) as executor:
            for delta in range(start_timedelta_days, end_timedelta_days + 1):
                executor.submit(get_and_write_data_with_prefix, delta, 0, object_version, fieldnames)
    else:
        for delta in range(start_timedelta_days, end_timedelta_days + 1):
            get_and_write_data_with_prefix(delta, 0, object_version, fieldnames)

