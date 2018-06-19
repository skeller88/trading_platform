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
        'app_create_timestamp']
    # nullable at database layer
    nullable_fields = [
        # response from APIs does not always include the time the data was retrieved by the exchange
        'exchange_timestamp',

        'db_id',
        'db_create_timestamp'
        'db_update_timestamp'
    ]

    def __init__(self, **kwargs):
        self.db_id = kwargs.get('db_id')
        self.db_update_timestamp = kwargs.get('db_update_timestamp')
        self.db_create_timestamp = kwargs.get('db_create_timestamp')

        self.currency = kwargs.get('currency')
        self.exchange_id = kwargs.get('exchange_id')
        self.free = kwargs.get('free')
        self.locked = kwargs.get('locked')
        self.total = kwargs.get('total')
        self.version = kwargs.get('version')
        self.exchange_timestamp = kwargs.get('exchange_timestamp')
        self.app_create_timestamp = kwargs.get('app_create_timestamp')

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
