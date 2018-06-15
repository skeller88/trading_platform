from trading_platform.exchanges.data.financial_data import zero


class Balance:
    """
    Balance of a particular asset on an exchange.

    Application (OLTP)
    - Determine the balances available for arbitraging, and how much to arbitrage per currency per exchange.

    Analytics (OLAP)
    - Track deltas in portfolio value to determine profitability of arbitrage strategy
    """
    # required fields at database layer
    required_fields = [
        'currency',
        'exchange_id',
        'free',
        'locked',
        'total',
        'version',
        'processing_time']
    # nullable at database layer
    nullable_fields = [
        # response from APIs does not always include the time the data was retrieved by the exchange
        'event_time',

        'db_id',
        'created_at'
        'updated_at'
    ]

    def __init__(self, **kwargs):
        self.db_id = kwargs.get('db_id')
        self.updated_at = kwargs.get('updated_at')
        self.created_at = kwargs.get('created_at')

        self.currency = kwargs.get('currency')
        self.exchange_id = kwargs.get('exchange_id')
        self.free = kwargs.get('free')
        self.locked = kwargs.get('locked')
        self.total = kwargs.get('total')
        self.version = kwargs.get('version')
        self.event_time = kwargs.get('event_time')
        self.processing_time = kwargs.get('processing_time')

    # https://stackoverflow.com/questions/390250/elegant-ways-to-support-equivalence-equality-in-python-classes
    def __eq__(self, other):
        """Overrides the default implementation"""
        if isinstance(self, other.__class__):
            return self.__dict__ == other.__dict__
        return NotImplemented

    def __hash__(self):
        """Overrides the default implementation"""
        return hash(tuple(sorted(self.__dict__.items())))

    @classmethod
    def instance_with_zero_value_fields(cls):
        """
        Instead of returning None, return a Balance instance with zero value fields. Makes app logic cleaner.

        Returns:

        """
        return cls(total=zero, free=zero, locked=zero)

    @staticmethod
    def classname():
        return 'balance'
