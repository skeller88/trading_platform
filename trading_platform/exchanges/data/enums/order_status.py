"""
Possible order statuses

pending - app will attempt to place an order

open - order has been successfully received by the exchange and placed on its order book

partially_filled - part of the order has been filled

cancelled - order was cancelled without being filled

cancelled_and_partially_filled - order was cancelled after part of the order was filled

filled - all of the order was filled
"""


class OrderStatus:
    pending = 0
    insufficient_order_size = 1
    open = 2
    partially_filled = 3
    cancelled = 4
    cancelled_and_partially_filled = 5
    filled = 6

    statuses_to_names = {
        'pending': 0,
        'insufficient_order_size': 1,
        'open': 2,
        'partially_filled': 3,
        'cancelled': 4,
        'cancelled_and_partially_filled': 5,
        'filled': 6,
    }

    @classmethod
    def from_exchange_string(cls, exchange_string: str):
        """
        Args:
            exchange_string:

        Returns: OrderStatus

        """
        if exchange_string == 'canceled':
            exchange_string = 'cancelled'

        return cls.statuses_to_names.get(exchange_string)

