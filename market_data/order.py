from copy import deepcopy

from market_data.enums import exchange_ids
from market_data.enums.order_side import OrderSide
from market_data.enums.order_status import OrderStatus
from market_data.enums.order_type import OrderType
from market_data.financial_data import FinancialData, zero
from market_data.pair import Pair
from utils.datetime_operations import utc_timestamp, microsecond_timestamp_to_second_timestamp

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

    Order on an exchange. Can be open, cancelled, partially filled, or filled. Each ArbitrageAttempt has two Orders
    associated with it. An Order that's open will have an OpenOrder associated with it. Associations occur via the
    order_index field.

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
    nullable_fields = [
        # database metadata
        'db_id',
        'created_at',
        'updated_at',

        # exchange-related metadata
        # Binance returns the timestamp of an order, Bittrex doesn't
        'event_time',
        
        # Cancelled orders and orders returned from the open_orders table won't have the following numerical fields:
        'amount',
        'filled',
        'price',
        'remaining',

        # Cancelled orders won't have order metadata. 
        'order_side',
        'order_type'
    ]

    required_fields = [
        # app metadata
        'processing_time',
        'version',

        # database metadata
        'order_index',

        # exchange-related metadata
        'exchange_id',
        'order_id',

        # order metadata.
        'base',
        'quote',
        'order_status',
    ]

    def __init__(self, **kwargs):
        """
        Nullable fields are
        - updated_at

        Fields that will be created by core.market_Data.order.Order constructor:
        - order_index
        - processing_time

        Fields that will be created by the database:
        - db_id
        - created_at
        - updated_at

        :param kwargs: Expected fields and their types
            # app metadata
            processing_time: str. Time when the order was processed by the arbitrage_bot.
            version: str

            # database metadata
            db_id: int
            order_index: str. Used to query an order in the database without the db id, so must be able to be constructed
            from exchange data alone. Also used to group multiple snapshots (database entities) of the same order over
            time. Example: "exchange-1-7754382".

            margin: float
            created_at: Decimal
            updated_at: Decimal

            # exchange-related metadata
            exchange_id: int. core/market_data/enums/exchange_ids.py
            event_time: Decimal. Time when the order was placed. Assumed to be in UTC.
            order_id: str. Id of the order on the exchange
            order_type: int. core/market_data/enums/order_type.py

            # order numerical data
            amount: str
            filled: str
            price: str
            remaining: str. Size of order remaining.

            # order metadata
            base: str
            quote: str
            order_status: int. core/market_data/enums/order_status.py
            order_side: int. Side
        """
        # app data
        processing_time = kwargs.get('processing_time')
        # Order instance could either be instantiated for the first time or populated with data from a DTO
        self.processing_time = processing_time if processing_time is not None else utc_timestamp()
        self.version = 0

        # database data
        self.db_id = kwargs.get('db_id')
        # Not unique, but all orders with this index will be associated with the same order on a given exchange.
        # Necessary to track the state of an order over time.
        self.order_index = '{0}-{1}'.format(kwargs.get('exchange_id'), kwargs.get('order_id'))
        self.created_at = kwargs.get('created_at')
        self.updated_at = kwargs.get('updated_at')

        # exchange-related data
        self.exchange_id = kwargs.get('exchange_id')
        self.event_time = kwargs.get('event_time')
        self.order_id = kwargs.get('order_id')
        self.order_type = kwargs.get('order_type')

        # order numerical data
        self.amount = FinancialData(kwargs.get('amount'))
        self.filled = FinancialData(kwargs.get('filled'))
        self.price = FinancialData(kwargs.get('price'))
        self.remaining = FinancialData(kwargs.get('remaining'))

        # order data
        self.base = kwargs.get('base')
        self.quote = kwargs.get('quote')
        self.order_status = kwargs.get('order_status')
        self.order_side = kwargs.get('order_side')

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
            'processing_time': self.processing_time,
            'version': self.version,

            'db_id': self.db_id,
            'order_index': self.order_index,
            'created_at': self.created_at,
            'updated_at': self.updated_at,

            'exchange_id': self.exchange_id,
            'event_time': self.event_time,
            'order_id': self.order_id,
            'order_type': self.order_type,

            'amount': self.amount,
            'filled': self.filled,
            'price': self.price,
            'remaining': self.remaining,

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
        copy.created_at = None
        copy.updated_at = None

        copy.processing_time = utc_timestamp()

        copy.filled = copy.amount
        copy.remaining = zero
        return copy

    @classmethod
    def financial_data_fields(cls):
        """
        Numpy will cast certain fields to an int when they should always have FinancialData-level precision
        So specify the types of these fields when reading Order data from a csv file.
        Returns:
        """
        return [
            'amount',
            'filled',
            'price',
            'remaining'
        ]


    @classmethod
    def csv_fieldnames(cls):
        return cls.required_fields + cls.nullable_fields

    @classmethod
    def standardize_exchange_data(cls, order_data, exchange_id=None):
        """
        Standardizes exchange data and returns a dict with the standardized data. Has logic to
        handle different exchanges.
        Args:
            order_data:
            exchange_id: Determines how standardization of certain fields will occur.

        Returns:

        """
        pair = Pair.from_exchange_client_string(order_data.get('symbol'))

        standardized = {
            # exchange-related data
            'exchange_id': exchange_id,
            'order_type': OrderType.from_exchange_data(order_data.get('type')),

            # numerical data
            'amount': FinancialData(order_data.get('amount')),
            'cost': FinancialData(order_data.get('cost')),
            'filled': FinancialData(order_data.get('filled')),
            'price': FinancialData(order_data.get('price')),
            'remaining': FinancialData(order_data.get('remaining')),

            # metadata
            'base': pair.base,
            'quote': pair.quote,
            # The exchange won't return the order status when the order is placed, so assume it's open
            'order_status': OrderStatus.open,
            'order_side': OrderSide.from_exchange_data(order_data.get('side'))
        }

        if exchange_id == exchange_ids.binance:
            # Binance has an orderId that is type float, and origClientOrderId that is type str. Documentation is lacking
            # but seems like origClientOrderId can be set client side, or auto-generated. Only need to send one of orderId
            # or origClientOrderId when querying or cancelling an order, for now anyway. Let's see if we get away with it:
            # https://www.binance.com/restapipub.html
            standardized['order_id'] = order_data.get('id')
        elif exchange_id == exchange_ids.bittrex:
            standardized['order_id'] = order_data.get('id')

        if not order_data.get('remaining'):
            standardized['remaining'] = order_data.get('amount')

        if order_data.get('timestamp'):
            standardized['event_time'] = microsecond_timestamp_to_second_timestamp(order_data.get('timestamp'))

        return standardized

    @staticmethod
    def classname():
        return 'order'
