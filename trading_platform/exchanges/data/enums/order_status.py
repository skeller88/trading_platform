"""
Possible order statuses

pending - app will attempt to place an order

open - order has been successfully received by the exchange and placed on its order book

partially_filled - part of the order has been filled

cancelled - order was cancelled without being filled

cancelled_and_partially_filled - order was cancelled after part of the order was filled

filled - all of the order was filled
"""
from typing import Dict

from trading_platform.exchanges.data.financial_data import FinancialData, zero


class OrderStatus:
    pending = 0
    insufficient_order_size = 1
    open = 2
    partially_filled = 3
    cancelled = 4
    cancelled_and_partially_filled = 5
    # ccxt refers to this as "closed". I think "filled" is more descriptive, plus some exchanges return "filled" in
    # their raw (pre-ccxt) response.
    filled = 6

    statuses_to_names: Dict[int, str] = {
        0: 'pending',
        1: 'insufficient_order_size',
        2: 'open',
        3: 'partially_filled',
        # British spelling of cancelled has two l's, American spelling has one l.
        4: 'cancelled',
        5: 'cancelled_and_partially_filled',
        6: 'filled',
    }

    @classmethod
    def from_exchange_data(cls, exchange_data: Dict):
        """
        Args:
            exchange_data:

        Returns: OrderStatus

        """
        order_status: str = exchange_data.get('status')

        if order_status == 'closed':
            return OrderStatus.filled

        is_partially_filled: bool = FinancialData(exchange_data.get('filled')) > zero

        if order_status == 'canceled':
            return OrderStatus.cancelled_and_partially_filled if is_partially_filled else OrderStatus.cancelled

        if order_status == cls.statuses_to_names.get(OrderStatus.open):
            return OrderStatus.partially_filled if is_partially_filled else OrderStatus.open

        raise Exception('No OrderStatus found for order_status {0}'.format(order_status))
