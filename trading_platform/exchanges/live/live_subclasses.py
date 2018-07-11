"""
An exchange client is "live" if it queries the actual exchange, not a disk or a stub. These methods are utility methods
to select all ExchangeClientServiceAbc live subclasses and fetch the API keys and secrets for these subclasses.
"""
from typing import List

from trading_platform.aws_utils.parameter_store_service import ParameterStoreService
from trading_platform.exchanges.live.binance_live_service import BinanceLiveService
from trading_platform.exchanges.live.bittrex_live_service import BittrexLiveService
from trading_platform.exchanges.live.gdax_live_service import GdaxLiveService
from trading_platform.exchanges.live.kraken_live_service import KrakenLiveService
from trading_platform.exchanges.live.kucoin_live_service import KucoinLiveService
from trading_platform.exchanges.live.poloniex_live_service import PoloniexLiveService

exchange_credentials_param = 'exchange_credentials'
test_exchange_credentials_param = 'test_exchange_credentials'


def get_all_live_exchange_service_credentials(param_name=exchange_credentials_param):
    """
    :param param_name:
    :return: {int: ExchangeClient}
    """
    return get_exchange_credentials_by_id(all_live(), param_name)


def exchange_service_credentials_for_exchange(exchange_service_subclass, param_name=exchange_credentials_param):
    credentials = ParameterStoreService.get_parameter(param_name=param_name)
    return credentials[exchange_service_subclass.exchange_name]


def get_exchange_credentials_by_id(exchange_service_subclasses, param_name):
    """
    :param exchange_service_subclasses:
    :param param_name: parameter name to fetch from AWS parameter store
    :return: dict of subset of credentials for exchange service subclasses
    """
    credentials = ParameterStoreService.get_parameter(param_name=param_name)
    return {subclass.exchange_id: credentials.get(subclass.exchange_name) for subclass in exchange_service_subclasses}


def instantiate_live_test_exchanges(withdrawal_fees_by_exchange_id=None):
    withdrawal_fees_by_exchange_id = withdrawal_fees_by_exchange_id
    return instantiate(mvp_live(), param_name=test_exchange_credentials_param,
                       withdrawal_fees_by_exchange=withdrawal_fees_by_exchange_id)


def instantiate(subclasses, param_name=exchange_credentials_param, withdrawal_fees_by_exchange=None):
    credentials = ParameterStoreService.get_parameter(param_name=param_name)
    withdrawal_fees_by_exchange = withdrawal_fees_by_exchange if withdrawal_fees_by_exchange is not None else {}
    exchange_services = {}
    for exchange_service_class in subclasses:
        name = exchange_service_class.exchange_name
        id = exchange_service_class.exchange_id
        credentials_for_exchange = credentials.get(name)
        if credentials_for_exchange is not None:
            exchange_services[id] = exchange_service_class(credentials_for_exchange.get('key'),
                                                           credentials_for_exchange.get('secret'),
                                                           withdrawal_fees=withdrawal_fees_by_exchange.get(id))
        else:
            exchange_services[id] = exchange_service_class(None, None, withdrawal_fees=None)
    return exchange_services


def all_live():
    """
    https://stackoverflow.com/questions/3862310/how-can-i-find-all-subclasses-of-a-class-given-its-name doesn't
    work if the variables aren't declared in local scope.
    :return:
    """
    return [BinanceLiveService, BittrexLiveService, GdaxLiveService, KucoinLiveService, KrakenLiveService,
            PoloniexLiveService]


def mvp_live():
    return [BittrexLiveService, BinanceLiveService]
