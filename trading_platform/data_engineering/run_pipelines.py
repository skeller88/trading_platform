from trading_platform.data_engineering.fetch_s3_ticker_objects import fetch_s3_ticker_objects

v4_fieldnames = [
    'ask',
    'bid',
    'last',
    'base',
    'quote',
    'exchange_id',
    'event_time',
    'processing_time',
    'version'
]


def s3_tickers_to_arbitrage_opportunities(start_timedelta_days, end_timedelta_days, ticker_version, ticker_fieldnames, multithreading):
    fetch_s3_ticker_objects(start_timedelta_days, end_timedelta_days, ticker_version, ticker_fieldnames, multithreading)


s3_tickers_to_arbitrage_opportunities(0, 4, '4', v4_fieldnames, multithreading=True)
