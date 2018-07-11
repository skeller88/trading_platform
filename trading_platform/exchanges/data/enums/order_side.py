"""
Enum representing buy side or sell side of an order.
"""


class OrderSide:
    buy = 0
    buy_str = 'buy'
    sell = 1
    sell_str = 'sell'

    @staticmethod
    def from_exchange_data(order_side_str):
        order_side_str = order_side_str.lower()

        if order_side_str == 'buy':
            return OrderSide.buy
        elif order_side_str == 'sell':
            return OrderSide.sell
        else:
            raise Exception('OrderSide not found for value {0}'.format(order_side_str))