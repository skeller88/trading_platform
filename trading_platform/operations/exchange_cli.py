"""
Interact with exchanges without logging in or running tests. Common operations include:
- Cancelling orders
- Checking balances
- Placing orders
- Checking order status
"""
import json
import os
from time import sleep

from trading_platform.exchanges.data.enums import exchange_ids
from trading_platform.exchanges.data.enums.order_side import OrderSide
from trading_platform.exchanges.data.enums.order_type import OrderType
from trading_platform.exchanges.data.financial_data import FinancialData
from trading_platform.exchanges.data.order import Order
from trading_platform.exchanges.data.pair import Pair
from trading_platform.exchanges.live import live_subclasses

profile = os.environ.get('AWS_PROFILE')
exchange_services_by_id = live_subclasses.instantiate(live_subclasses.all_live())
binance = exchange_services_by_id.get(exchange_ids.binance)
bittrex = exchange_services_by_id.get(exchange_ids.bittrex)
kucoin = exchange_services_by_id.get(exchange_ids.kucoin)


def cancel_orders(pair):
    """
    Cancel any orders that weren't cancelled by the tests
    Returns:

    """
    # exchange_services_by_id = live_subclasses.instantiate(live_subclasses.mvp_live())

    for exchange in exchange_services_by_id.values():
        open_orders = exchange.fetch_open_orders(pair)
        for order_id, order in open_orders.items():
            print('Cancelling order', order_id)
            exchange.cancel_order(order=order.exchange_order_id)


def fetch_balances():
    """
    Cancel any orders that weren't cancelled by the tests
    Returns:

    """
    # exchange_services_by_id = live_subclasses.instantiate(live_subclasses.mvp_live())
    for exchange in exchange_services_by_id.values():
        balances = exchange.fetch_balances()
        print('\n', exchange.exchange_name)
        for currency, balance in balances.items():
            print(currency, balance.free)


pair = Pair(base='USDT', quote='BTC')
# pair = Pair(base='BTC', quote='ZEN')
pair = Pair(base='BTC', quote='ETH')

order: Order = Order(**{
    # app metadata
    'version': Order.current_version,

    # exchange-related metadata
    'exchange_id': exchange_ids.bittrex,
    'order_type': OrderType.limit,
    'order_side': OrderSide.sell,

    # order metadata
    'base': pair.base,
    'quote': pair.quote,

    'amount': FinancialData(0.0446458),
    'price': FinancialData(.06),
})

# with open('/Users/shanekeller/Documents/trading_platform/trading_platform/exchanges/data/cryptocurrencies.json', 'r') as f:
#     crypto_json: str = json.load(f)
#
#     for market in crypto_json.keys():
#         for exchange in [bittrex, binance]:
#             dd = exchange.fetch_deposit_destination(market)
#
#             if dd is not None and dd.status != 'ok':
#                 print(market, exchange.exchange_name, dd.status, '\n')

while True:
    markets = binance.get_client().load_markets(reload=True)
    # list(map(print, markets))
    markets = bittrex.get_client().load_markets(reload=True)

    list(map(print, markets))
    sleep(1)

# bittrex.fetch_balances()
# print(bittrex.get_balance('BTC').free)
# order_resp = bittrex.create_limit_sell_order(order)
# print(order_resp.__dict__)

# order = bittrex.cancel_order(order=order)
# print(order.exchange_order_id)

# trades = bittrex.fetch_orders(pair=Pair(base='BTC', quote='GTO'))
# for trade in trades:
#     print(trade)

# order = bittrex.fetch_order(exchange_order_id='54ee8a42-0354-423e-9d23-8226c4a8e9c7', pair=pair)
# print(order.__dict__)


# order = kucoin.fetch_order(exchange_order_id='5b357eca87dcdf1045a51e9c', pair=pair, params={'type': OrderSide.buy_str})
# orders = kucoin.fetch_closed_orders(pair=Pair(base='USDT', quote='BTC'))
# print(order)
# orders = bittrex.fetch_open_orders(pair=pair)

# list(map(lambda x: print(x[0], x[1].exchange_order_id), orders.items()))
# list(map(lambda x: print(x[0], x[1].free), bittrex.fetch_balances().items()))


# Uncomment the desired operation
# fetch_balances()
# fetch_closed_orders()


# order = fetch_order(exchange_order_id=19269522, symbol=Pair(base='ETH', quote='OMG').name_for_exchange_clients, exchange_id=exchange_ids.binance)
# for k, v in order.items():
#     print(k, v, '\n')
