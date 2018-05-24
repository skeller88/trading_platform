"""
Generates test data for testing purposes.
"""
from copy import copy
from decimal import Decimal

from exchanges.src.data.balance import Balance
from exchanges.src.data.enums import exchange_ids
from exchanges.src.data.enums.order_side import OrderSide
from exchanges.src.data.enums.order_status import OrderStatus
from exchanges.src.data.enums.order_type import OrderType
from exchanges.src.data.financial_data import FinancialData, one
from exchanges.src.data.order import Order
from exchanges.src.data.pair import Pair
from exchanges.src.data.ticker import Ticker
from utils.src import datetime_operations
from utils.src.datetime_operations import utc_timestamp, seconds_per_hour

decimal_num = Decimal(10)
pair = Pair(base='USDT', quote='ETH')
now = utc_timestamp()

percent_balance_to_trade = FinancialData(90)

# Assume that these minimum balances are kept on exchanges for testing purposes
minimum_eth_balance = FinancialData(.1)
minimum_usdt_balance = FinancialData(50)


def quote_buy_and_sell_prices(exchange_service, pair):
    """
    The exchanges don't expose test order endpoints, and tests shouldn't place orders that are filled. Therefore,
    set the buy price to 80% of the current ask and the sell price to 120% of the current bid to make sure that the
    orders aren't filled.
    Args:
        exchange_service ExchangeServiceAbc:
        pair Pair:

    Returns:

    """
    exchange_service.fetch_latest_tickers()
    quote_ticker = exchange_service.get_ticker(pair.name)
    quote_sell_price = quote_ticker.ask * (one + FinancialData(.2))
    quote_buy_price = quote_ticker.bid * (one - FinancialData(.2))
    return {
        'quote_ticker': quote_ticker,
        'buy_price': quote_buy_price,
        'sell_price': quote_sell_price
    }


def balance(exchange_id):
    kwargs = {
        'db_id': None,

        'currency': 'ETH',
        'exchange_id': exchange_id,
        'free': FinancialData(10),
        'locked': FinancialData(5),
        'total': FinancialData(15),
        'version': 0,
        'event_time': now,
        'processing_time': now,
    }

    return Balance(**kwargs)


def order(exchange_id=exchange_ids.bittrex, order_status=OrderStatus.open, order_side=OrderSide.buy,
          processing_time=None, numerical_fields=True):
    processing_time = datetime_operations.utc_timestamp() if processing_time is None else processing_time
    kwargs = {
        # app metadata
        'processing_time': processing_time,
        'version': Order.current_version,

        # database metadata
        'db_id': None,
        'created_at': None,
        'updated_at': None,

        # exchange-related metadata

        'exchange_id': exchange_id,
        'event_time': processing_time - 86000,
        'order_id': str(processing_time),
        'order_type': OrderType.limit,

        # order metadata
        'base': 'USDT',
        'quote': 'NEO',
        'order_status': order_status,
        'order_side': order_side
    }

    if numerical_fields:
        # order numerical data
        kwargs['amount'] = decimal_num
        kwargs['cost'] = decimal_num
        kwargs['fee'] = decimal_num
        kwargs['filled'] = decimal_num
        kwargs['price'] = decimal_num
        kwargs['remaining'] = decimal_num

    return Order(**kwargs)


def high_low_tickers():
    """
    "high" Ticker has higher bid and ask than the "low" ticker.
    :return:
    """
    base_kwargs = {
        'base': pair.base,
        'exchange_id': exchange_ids.bittrex,
        'event_time': now,
        'quote': pair.quote,
        'db_id': None,
        'processing_time': now,
        'version': Ticker.current_version
    }

    high_kwargs = copy(base_kwargs)
    high_kwargs['ask'] = 5
    high_kwargs['bid'] = 4
    high_kwargs['last'] = 4
    high = Ticker(**high_kwargs)

    low_kwargs = copy(base_kwargs)
    low_kwargs['ask'] = 3
    low_kwargs['bid'] = 1
    low_kwargs['last'] = 2
    low = Ticker(**low_kwargs)

    return {
        'high': high,
        'low': low
    }


def time_ordered_tickers():
    """
    "first" Ticker was created before the "second" Ticker.
    :return:
    """
    base_kwargs = {
        'base': pair.base,
        'exchange_id': exchange_ids.bittrex,
        'event_time': now,
        'quote': pair.quote,
        'db_id': None,
        'processing_time': now,
        'version': Ticker.current_version
    }

    first_kwargs = copy(base_kwargs)
    first_kwargs['ask'] = 5
    first_kwargs['bid'] = 4
    first_kwargs['last'] = 4
    first = Ticker(**first_kwargs)

    second_kwargs = copy(base_kwargs)
    second_kwargs['ask'] = 3
    second_kwargs['bid'] = 1
    second_kwargs['last'] = 2
    second_kwargs['event_time'] = second_kwargs['event_time'] + seconds_per_hour
    second = Ticker(**second_kwargs)

    return [first, second]


def print_unequal_value(self, other):
    """
    Utility method for debugging test failures.
    :param self:
    :param other:
    :return:
    """
    for key, value in self.__dict__.items():
        if value != other.__dict__[key]:
            print(key, value, other.__dict__[key])