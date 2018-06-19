from copy import deepcopy
from typing import Dict

from trading_platform.exchanges.data.enums import exchange_ids
from trading_platform.exchanges.data.enums.order_side import OrderSide
from trading_platform.exchanges.data.enums.order_status import OrderStatus
from trading_platform.exchanges.data.enums.order_type import OrderType
from trading_platform.exchanges.data.financial_data import FinancialData, zero
from trading_platform.exchanges.data.pair import Pair
from trading_platform.utils.datetime_operations import utc_timestamp, microsecond_timestamp_to_second_timestamp

STRFTIME_MICROSECONDS = '%Y-%m-%dT%H:%M:%SZ'


class Order:
    """
    # TODO - consolidate this docstring with SqlAlchemyOpenOrderDto
    Example orders table state:
    UUID        - pair_name - filled - total - order_status
    bittrex-123 - eth-xmr - 0 - 10 - pending
    bittrex-123 - eth-xmr - 0 - 10 - open
    binance-567 - eth-powr - 5 - 10 - partially_filled
    bittrex-123 - eth-xmr - 10 - 10 - filled
    binance-567 - eth-powr - 5 - 10 - cancelled

    Order on an exchange. Can be open, cancelled, partially filled, or filled.

    Example of an open order:
    [{'info': {
        'orderNumber': '80937015089', 'type': 'limit', 'rate': '4.00000000', 'startingAmount': '2.00000000',
        'amount': '2.00000000', 'total': '8.00000000', 'date': '2018-01-04 00:17:24', 'margin': 0, 'order_status': 'open',
        'order_side': 'buy', 'price': '4.00000000'
    },
    'id': '80937015089', 'timestamp': 1515025044000, 'datetime': '2018-01-04T00:17:24.000Z', 'order_status': 'open',
    'symbol': 'DASH/USDT', 'type': 'limit', 'order_side': 'buy', 'price': 4.0, 'cost': 8.0, 'amount': 2.0, 'filled': 0.0,
    'remaining': 2.0, 'trades': None, 'fee': None
    }]

    Another example:
    {'info': {'timestamp': 1515881912541, 'order_status': 'open', 'type': 'limit', 'order_side': 'buy', 'price': 15.0,
    'amount': 2.6666666666666665, 'orderNumber': '157533595862', 'resultingTrades': []}, 'id': '157533595862',
    'timestamp': 1515881912541, 'datetime': '2018-01-13T22:18:33.541Z', 'order_status': 'open', 'symbol': 'ETH/USDT',
    'type': 'limit', 'order_side': 'buy', 'price': 15.0, 'cost': 0.0, 'amount': 2.6666666666666665, 'filled': 0.0,
    'remaining': 2.6666666666666665, 'trades': [], 'fee': None}
    """
    current_version = 0
    # The properties in **kwargs that can be null. Note that this is different from the fields that can be null at
    # the database layer
    # No way to reliably get all of the fields of an object so they have to be tracked:
    # https://stackoverflow.com/questions/21945067/how-to-list-all-fields-of-a-class-in-python-and-no-methods
    required_fields = [
        # exchange-related metadata
        'exchange_id',
        'base',
        'quote',

        # order metadata.
        'strategy_execution_id',
        'order_id',
        'version',
        'app_create_timestamp',
        'order_status',
    ]

    # Numpy will cast certain fields to an int when they should always have FinancialData-level precision
    # So specify the types of these fields when reading Order data from a csv file.
    # Returns:
    financial_data_fields = [
        'amount',
        'filled',
        'price',
        'remaining'
    ]

    index_fields = [
        'strategy_execution_id',
        'exchange_id',
        'quote',
        'base',
        'order_side',
        'price',
        'amount'
    ]

    nullable_fields = [
        # database metadata
        'db_id',
        'db_create_timestamp',
        'db_update_timestamp',

        # exchange-related metadata
        # Binance returns the timestamp of an order, Bittrex doesn't
        'exchange_timestamp',

        # Cancelled orders and orders returned from the open_orders table won't have the following numerical fields:
        'amount',
        'filled',
        'price',
        'remaining',
        'params,'

        # Cancelled orders won't have order metadata. 
        'order_side',
        'order_type',

        # Pending orders won't have the following fields:
        'exchange_order_id',
    ]

    def __init__(self, **kwargs):
        """
        Nullable fields are
        - db_update_timestamp

        Fields that will be created by core.market_Data.order.Order constructor:
        - order_id
        - app_create_timestamp

        Fields that will be created by the database:
        - db_id
        - db_create_timestamp
        - db_update_timestamp

        :param kwargs: Expected fields and their types
            # app metadata
            app_create_timestamp: str. Time when the order was processed by the arbitrage_bot.
            version: str

            # database metadata
            db_id: int
                    #
            order_id: str. Not unique, but all orders with this index will be associated with the same order on a
                given exchange. Used to query an order in the database without the db id, so must be able to be constructed
                from exchange data alone. Also used to group multiple snapshots (database entities) and track the state of
                an order over time. Example: "exchange-1-7754382".

                Can be either "exchange_id-exchange_order_id" or "[exchange_id]_[quote]_[base]_[order_type]_[price]_[amount]"

            margin: float
            db_create_timestamp: Decimal
            db_update_timestamp: Decimal

            # exchange-related metadata
            exchange_id: int. core/market_data/enums/exchange_ids.py
            exchange_timestamp: Decimal. Time when the order was placed. Assumed to be in UTC.
            exchange_order_id: str. Id of the order on the exchange
            order_type: int. core/market_data/enums/order_type.py

            # order numerical data
            amount: str
            filled: str
            price: str
            remaining: str. Size of order remaining.
            params: Dict. Order parameters.

            # order metadata
            base: str
            quote: str
            order_status: int. core/market_data/enums/order_status.py
            order_side: int. Side
        """
        # app data
        app_create_timestamp = kwargs.get('app_create_timestamp')
        # Order instance could either be instantiated for the first time or populated with data from a DTO
        self.app_create_timestamp = app_create_timestamp if app_create_timestamp is not None else utc_timestamp()
        self.version = kwargs.get('version') if kwargs.get('version') is not None else 0
        self.strategy_execution_id = kwargs.get('strategy_execution_id', 0)

        # database data
        self.db_id = kwargs.get('db_id')
        self.db_create_timestamp = kwargs.get('db_create_timestamp')
        self.db_update_timestamp = kwargs.get('db_update_timestamp')

        # exchange-related data
        self.exchange_id = kwargs.get('exchange_id')
        self.exchange_timestamp = kwargs.get('exchange_timestamp')
        self.exchange_order_id = kwargs.get('exchange_order_id')
        self.order_type = kwargs.get('order_type')

        # order numerical data
        self.amount = FinancialData(kwargs.get('amount'))
        self.filled = FinancialData(kwargs.get('filled'))
        self.price = FinancialData(kwargs.get('price'))
        self.remaining = FinancialData(kwargs.get('remaining'))
        self.params = kwargs.get('params')

        # order data
        self.base = kwargs.get('base')
        self.quote = kwargs.get('quote')
        self.order_status = kwargs.get('order_status')
        self.order_side = kwargs.get('order_side')

        order_id = kwargs.get('order_id')

        if order_id is not None:
            self.order_id = order_id
        else:
            self.order_id = '_'.join(map(lambda field: str(getattr(self, field)), self.index_fields))
        # comment out for now because I don't want to deal with the Order in run_backtest having all of the required
        # fields
        # check_required_fields(self)

    # https://stackoverflow.com/questions/390250/elegant-ways-to-support-equivalence-equality-in-python-classes
    def __eq__(self, other):
        """Overrides the default implementation"""
        if isinstance(self, other.__class__):
            for k, v in self.__dict__.items():
                if self.__dict__.get(k) != other.__dict__.get(k):
                    print('Instance attribute {0}: expected {1}, got {2}'.format(k, v, other.__dict__.get(k)))
                    return False
        return True

    def __hash__(self):
        """Overrides the default implementation"""
        return hash(tuple(sorted(self.__dict__.items())))

    def to_dict(self):
        return {
            'app_create_timestamp': self.app_create_timestamp,
            'version': self.version,

            'db_id': self.db_id,
            'order_id': self.order_id,
            'db_create_timestamp': self.db_create_timestamp,
            'db_update_timestamp': self.db_update_timestamp,

            'exchange_id': self.exchange_id,
            'exchange_timestamp': self.exchange_timestamp,
            'exchange_order_id': self.exchange_order_id,
            'order_type': self.order_type,

            'amount': self.amount,
            'filled': self.filled,
            'price': self.price,
            'remaining': self.remaining,
            'params': self.params,

            'base': self.base,
            'quote': self.quote,
            'order_status': self.order_status,
            'order_side': self.order_side
        }

    def filled_order_copy(self):
        """
        Construct a filled order instance from the current instance by changing several fields. Used to save a filled
        order to the database based on the initial state of the order.

        Returns Order: copy of current instance with certain fields modified.
        """
        copy = deepcopy(self)
        copy.order_status = OrderStatus.filled
        # A new instance needs to be saved to the db.
        copy.db_id = None
        copy.db_create_timestamp = None
        copy.db_update_timestamp = None

        copy.app_create_timestamp = utc_timestamp()

        copy.filled = copy.amount
        copy.remaining = zero
        return copy

    def copy_updated_with_create_or_cancel_order_exchange_response(self, order_data: Dict):
        """
        Construct an open order instance that's a copy of the current instance, but with certain fields
        overwritten by the values in order_data from a create_limit_*_order or cancel_order exchange response.

        This method exists because the data returned from an exchange
        for a given Order may:
        1) be different from the values of an Order instance.
        2) not include all of the Order metadata. For example, Bittrex's create_limit_buy_order call does not return
        order numerical data.

        There are some differences in exchange create limit order responses.
        - Binance sets the "filled" and "remaining" fields. Bittrex doesn't.

        the exchange data returned by the create_limit call is different from the
        # exchange data returned by the fetch_open_orders call.

        Args:
            order_data:

        Returns:
            copy: Order

        """
        copy: Order = deepcopy(self)
        copy.exchange_order_id = order_data.get('id')
        copy.order_status = OrderStatus.open
        copy.app_create_timestamp = utc_timestamp()

        if order_data.get('timestamp'):
            copy.exchange_timestamp = microsecond_timestamp_to_second_timestamp(order_data.get('timestamp'))

        def overwrite_field_with_exchange_data(field):
            value = order_data.get(field)
            if value is not None:
                instance_field_value = getattr(copy, field)
                # TODO - print via logger.error instead
                if value != instance_field_value:
                    print('ERROR - order field {0} - instance value is {1}, exchange_data value is {2}'.format(field, value,
                                                                                                       instance_field_value))
                elif instance_field_value is None:
                    print('ERROR - order field {0} - instance value and exchange_data value is None'.format(field))
                setattr(copy, field, value)

        [overwrite_field_with_exchange_data(field) for field in self.financial_data_fields]
        return copy

    @classmethod
    def from_fetch_order_exchange_response(cls, order_data, exchange_id=None):
        """
        Converts exchange fetch_*_order response to an Order instance. Has logic to handle different exchanges.
        See exchange_data.py for example response format.

        Unlike copy_updated_with_create_or_cancel_order_exchange_response, this method is not a copy of an
        existing Order instance that is updated with exchange data. That's because the app may not have the metadata
        for an order that's being fetched.

        Args:
            order_data:
            exchange_id: Determines how standardization of certain fields will occur.

        Returns: Order

        """
        amount: FinancialData = order_data.get('amount')
        remaining: FinancialData = order_data.get('remaining')
        kwargs = {
            'exchange_id': exchange_id,
            'exchange_order_id': order_data.get('id'),
            'order_side': OrderSide.from_exchange_data(order_data.get('side')),
            'order_status': OrderStatus.from_exchange_data(order_data),
            'order_type': OrderType.limit,

            # numerical data
            'amount': FinancialData(amount),
            'cost': FinancialData(order_data.get('cost')),
            'filled': FinancialData(order_data.get('filled')),
            'price': FinancialData(order_data.get('price')),
            'remaining': remaining if remaining is not None else amount,
            'average': FinancialData(order_data.get('average')),
        }

        if order_data.get('symbol'):
            pair: Pair = Pair.from_exchange_client_string(order_data.get('symbol'))
            if pair:
                kwargs['base'] = pair.base
                kwargs['quote'] = pair.quote

        if order_data.get('timestamp'):
            kwargs['exchange_timestamp'] = microsecond_timestamp_to_second_timestamp(order_data.get('timestamp'))

        return cls(**kwargs)

    @classmethod
    def csv_fieldnames(cls):
        return cls.required_fields + cls.nullable_fields

    @staticmethod
    def classname():
        return 'order'
