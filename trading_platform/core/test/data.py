"""
Generates test data for testing purposes.
"""
from copy import copy
from decimal import Decimal

from trading_platform.exchanges.data.balance import Balance
from trading_platform.exchanges.data.enums import exchange_ids
from trading_platform.exchanges.data.enums.order_side import OrderSide
from trading_platform.exchanges.data.enums.order_status import OrderStatus
from trading_platform.exchanges.data.enums.order_type import OrderType
from trading_platform.exchanges.data.financial_data import FinancialData, one
from trading_platform.exchanges.data.order import Order
from trading_platform.exchanges.data.pair import Pair
from trading_platform.exchanges.data.ticker import Ticker
from trading_platform.utils import datetime_operations
from trading_platform.utils.datetime_operations import utc_timestamp, seconds_per_hour

decimal_num = Decimal(10)
pair = Pair(base='USDT', quote='ETH')
now = utc_timestamp()

percent_balance_to_trade = FinancialData(90)

# Assume that these minimum balances are kept on exchanges for testing purposes
minimum_eth_balance = FinancialData(.1)
minimum_usdt_balance = FinancialData(50)

# Calculate taxes assuming profits of around $400K in a year
# CA doesn't provide exemptions for long term capital gains:
# https://www.nerdwallet.com/ask/question/what-are-ca-state-tax-implications-on-long-term-capital-gains-27615
# https://www.tax-brackets.org/californiataxtable
# It would be tedious to add up all the marginal tax rates, so use a slightly lower % than would be used otherwise
ca_tax = FinancialData(.08)
federal_ltcg_tax = FinancialData(.15)
# https://www.fool.com/taxes/2018/01/05/what-are-the-new-and-improved-2018-tax-brackets.aspx
federal_income_tax = FinancialData(.35)

eth_withdrawal_fee = FinancialData(.008)
eth_price_usd = FinancialData(850)

class Defaults:
    ltcg_tax = federal_ltcg_tax + ca_tax
    income_tax = federal_income_tax + ca_tax

    # Average of Binance and Bittrex trade fees: binance - .001, bittrex - .0025
    trade_fee = FinancialData(0.002)
    arb_spread = FinancialData(.01)

    # defaults based on DASH_ETH market data
    # ETH as base, withdrawal fee on binance is .01, on bittrex is .006, so assuming that withdrawals will occur from both
    # exchanges, take the average withdrawal fee.
    initial_ticker = FinancialData(.5)
    usdt_withdrawal_fee = FinancialData(9)
    base_withdrawal_fee = eth_withdrawal_fee
    base_withdrawal_fee_in_quote = base_withdrawal_fee / initial_ticker
    quote_withdrawal_fee = FinancialData(.002)
    initial_base_capital = FinancialData(20)
    initial_quote_capital = FinancialData(40)

# tickers in USD
tickers_to_usd = {
    'BTC': FinancialData(8000),
    'ETH': FinancialData(600),
    'USDT': one,
    'USD': one
}

markets = {
    # Profitable
    'POWR_ETH': {
        'base_withdrawal_fee': eth_withdrawal_fee,
        'quote_withdrawal_fee': 5,
        'initial_ticker': 0.00068001,
        'num_arbs_per_year': 880,
        'median_spread': 0.008
    },
    'QTUM_ETH': {
        'base_withdrawal_fee': eth_withdrawal_fee,
        'quote_withdrawal_fee': .01,
        'initial_ticker': 0.02910537,
        'num_arbs_per_year': 772,
        'median_spread': 0.0056
    },
    'LTC_ETH': {
        'base_withdrawal_fee': eth_withdrawal_fee,
        'quote_withdrawal_fee': .01,
        'initial_ticker': 0.26176,
        'num_arbs_per_year': 730,
        'median_spread': 0.0153
    },
    'ETC_ETH': {
        'base_withdrawal_fee': eth_withdrawal_fee,
        'quote_withdrawal_fee': .01,
        'initial_ticker': 0.00045985,
        'num_arbs_per_year': 472,
        'median_spread': 0.0064
    },
    'XLM_ETH': {
        'base_withdrawal_fee': eth_withdrawal_fee,
        'quote_withdrawal_fee': .01,
        'initial_ticker': 0.00045985,
        'num_arbs_per_year': 365,
        'median_spread': 0.0074
    },
    # Probably not
    'DASH_ETH': {
        'base_withdrawal_fee': eth_withdrawal_fee,
        'quote_withdrawal_fee': .002,
        'initial_ticker': 0.68583957,
        'num_arbs_per_year': 40,
        'median_spread': 0.005
    },
    'XMR_ETH': {
        'base_withdrawal_fee': eth_withdrawal_fee,
        'quote_withdrawal_fee': .04,
        'initial_ticker': 0.27164833,
        'num_arbs_per_year': 42,
        'median_spread': 0.0133
    },
    'ZEC_ETH': {
        'base_withdrawal_fee': eth_withdrawal_fee,
        'quote_withdrawal_fee': .005,
        'initial_ticker': 0.46480849,
        'num_arbs_per_year': 42,
        'median_spread': 0.0058
    }
}


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
        'exchange_timestamp': now,
        'app_create_timestamp': now,
    }

    return Balance(**kwargs)


def order(exchange_id=exchange_ids.bittrex, order_status=OrderStatus.open, order_side=OrderSide.buy,
          strategy_execution_id='0', app_create_timestamp=None, numerical_fields=True):
    app_create_timestamp = datetime_operations.utc_timestamp() if app_create_timestamp is None else app_create_timestamp
    kwargs = {
        # app metadata
        'app_create_timestamp': app_create_timestamp,
        'version': Order.current_version,

        # database metadata
        'db_id': None,
        'db_create_timestamp': None,
        'db_update_timestamp': None,

        'strategy_execution_id': strategy_execution_id,

        # exchange-related metadata
        'exchange_id': exchange_id,
        'exchange_timestamp': app_create_timestamp - 86000,
        'exchange_order_id': str(app_create_timestamp),
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
        'exchange_timestamp': now,
        'quote': pair.quote,
        'db_id': None,
        'app_create_timestamp': now,
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
        'quote': pair.quote,

        'base_volume': FinancialData(1.23),
        'quote_volume': FinancialData(4.89123),

        'exchange_id': exchange_ids.bittrex,
        'exchange_timestamp': now,
        'db_id': None,
        'app_create_timestamp': now,
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
    second_kwargs['exchange_timestamp'] = second_kwargs['exchange_timestamp'] + seconds_per_hour
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