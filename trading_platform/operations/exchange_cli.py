"""
Interact with exchanges without logging in or running tests. Common operations include:
- Cancelling orders
- Checking balances
- Placing orders
"""
from trading_platform.exchanges.data.enums import exchange_ids
from trading_platform.exchanges.data.enums.order_side import OrderSide
from trading_platform.exchanges.data.pair import Pair
from trading_platform.exchanges.live import live_subclasses

exchange_services_by_id = live_subclasses.instantiate(live_subclasses.mvp_live())


def cancel_orders():
    """
    Cancel any orders that weren't cancelled by the tests
    Returns:

    """
    # exchange_services_by_id = live_subclasses.instantiate(live_subclasses.mvp_live())

    for exchange in exchange_services_by_id.values():
        open_orders = exchange.fetch_open_orders()
        for order_index, order in open_orders.items():
            print('Cancelling order', order_index)
            exchange.cancel_order(pair=Pair(base=order.base, quote=order.quote),
                                  order_id=order.order_id)


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


def execute(exchange_id, method_name, **params):
    exchange = exchange_services_by_id.get(exchange_id)
    method = getattr(exchange,  method_name)
    return method(**params)


def create_limit_order(exchange_id, order_side, pair, amount, price):
    exchange = exchange_services_by_id.get(exchange_id)

    if order_side == OrderSide.buy:
        order = exchange.create_limit_buy_order(pair, amount, price)
    else:
        order = exchange.create_limit_sell_order(pair, amount, price)

    print(order)


print(execute(exchange_ids.bittrex, 'fetch_deposit_destination', currency='ZEN', params={}))
# Uncomment the desired operation
# cancel_orders()
# fetch_balances()
# create_limit_order(exchange_ids.binance, order_side=OrderSide.sell, pair=Pair(base='ETH', quote='OMG'), price=FinancialData(0.01), amount=2.7972)
# fetch_closed_orders()


# order = fetch_order(order_id=19269522, symbol=Pair(base='ETH', quote='OMG').name_for_exchange_clients, exchange_id=exchange_ids.binance)
# for k, v in order.items():
#     print(k, v, '\n')

