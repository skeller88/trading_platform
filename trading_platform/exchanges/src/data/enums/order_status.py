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
    open = 0
    partially_filled = 1
    cancelled = 2
    cancelled_and_partially_filled = 3
    filled = 4

    statuses_to_names = {
        0: 'open',
        1: 'partially_filled',
        2: 'cancelled',
        3: 'cancelled_and_partially_filled',
        4: 'filled'
    }

