"""
Run the lambda. This script can only be run from the root directory.
"""
import os.path
import sys
import time

# Append the directory that is running this script. Otherwise 'core' module won't be discoverable because
# the 'core' module isn't added to the sys.path
sys.path.append(os.getcwd())
sys.path.append(os.getcwd().replace('ticker_fetcher', ''))
from trading_platform.exchanges.live import live_subclasses
from trading_platform.exchanges.ticker_service import TickerService


def main(event, context):
    start = time.time()
    exchange_services = live_subclasses.instantiate(subclasses=live_subclasses.all_live())
    filepath, tickers = TickerService.fetch_latest_tickers_and_save(exchange_services)
    print('wrote {0} tickers to {1}'.format(len(tickers), filepath))
    end = time.time()
    print('time elapsed (sec):', end - start)


if __name__ == '__main__':
    main(None, None)