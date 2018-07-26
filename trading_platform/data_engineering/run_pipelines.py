import os

from trading_platform.core.services.file_service import FileService
from trading_platform.data_engineering.ticker_etl_service import TickerEtlService

v4_fieldnames = [
    'ask',
    'bid',
    'last',
    'base',
    'quote',
    'exchange_id',
    'exchange_timestamp',
    'app_create_timestamp',
    'version'
]

relative_dir: str = 'trading_platform/trading_platform/data_engineering'
ticker_etl_service = TickerEtlService(FileService())


def aggregate():
    input_dir: str = os.path.dirname(__file__).replace(relative_dir, 'trading_system_data/tickers/standardized')
    output_dir: str = os.path.dirname(__file__).replace(relative_dir, 'trading_system_data/tickers/aggregated/minute')
    ticker_etl_service.aggregate(input_dir, output_dir)


def standardize():
    input_dir: str = os.path.dirname(__file__).replace(relative_dir, 'trading_system_data/tickers/raw')
    output_dir: str = os.path.dirname(__file__).replace(relative_dir, 'trading_system_data/tickers/standardized')
    print(input_dir, output_dir)
    ticker_etl_service.run_pipeline(input_dir, output_dir, [ticker_etl_service.standardize])


# standardize()
aggregate()