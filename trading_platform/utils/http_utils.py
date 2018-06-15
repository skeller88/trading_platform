import traceback
from time import sleep

import ccxt
import requests
import urllib3

# Exchanges are flakey. Hardcode the max number of retries for now
MAX_RETRIES = 3
# Hardcode sleep as well
SLEEP_SEC_BETWEEN_RETRIES = 3


def make_api_request(method, *args):
    print('executing {0}'.format(method.__name__))
    recent_error = None
    for retry in range(MAX_RETRIES):
        if retry > 0:
            sleep(SLEEP_SEC_BETWEEN_RETRIES)
            print('retry attempt number {0}'.format(retry))
        try:
            return method(*args)
        except (requests.HTTPError,
                ccxt.DDoSProtection,
                ccxt.ExchangeError,
                ccxt.ExchangeNotAvailable,
                ccxt.RequestTimeout,
                urllib3.exceptions.ReadTimeoutError
                ) as request_error:
            recent_error = request_error
            print('error when executing {0}'.format(method.__name__))
            traceback.print_exc()
            continue
    else:
        raise recent_error


def make_api_limit_order_request(method, symbol, amount, price, params):
    print('executing {0}'.format(method.__name__))
    recent_error = None
    for retry in range(MAX_RETRIES):
        if retry > 0:
            sleep(SLEEP_SEC_BETWEEN_RETRIES)
            print('retry attempt number {0}'.format(retry))
        try:
            return method(symbol, amount, price, params)
        except (requests.HTTPError,
                ccxt.DDoSProtection,
                ccxt.ExchangeError,
                ccxt.ExchangeNotAvailable,
                ccxt.RequestTimeout,
                ccxt.InvalidOrder,
                urllib3.exceptions.ReadTimeoutError
                ) as request_error:
            recent_error = request_error
            print('error when executing {0}'.format(method.__name__))
            traceback.print_exc()
            continue
    else:
        raise recent_error
