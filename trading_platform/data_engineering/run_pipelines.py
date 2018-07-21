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
input_dir: str = os.path.dirname(__file__).replace(relative_dir, 'trading_system_data/tickers')
output_dir: str = os.path.dirname(__file__).replace(relative_dir, 'trading_system_data/tickers_by_exchange_and_pair')

print(input_dir, output_dir)
ticker_etl_service = TickerEtlService(FileService())
ticker_etl_service.by_exchange_and_pair(input_dir, output_dir)