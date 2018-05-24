import traceback
from time import sleep

import ccxt
import requests
import urllib3
from ccxt import InvalidOrder

# Exchanges are flakey. Hardcode the max number of retries for now
MAX_RETRIES = 3
# Hardcode sleep as well
SLEEP_SEC_BETWEEN_RETRIES = 3


def make_api_request(err_msg, method, *args):
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
            print(err_msg)
            traceback.print_exc()
            continue
    else:
        raise recent_error


def make_api_limit_order_request(err_msg, method, symbol, amount, price, *params):
    try:
        return method(symbol, amount, price, *params)
    except (requests.HTTPError, ccxt.RequestTimeout, InvalidOrder) as error:
        print(err_msg, error)
        return