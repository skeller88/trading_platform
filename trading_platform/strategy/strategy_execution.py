from typing import Dict

from trading_platform.utils.datetime_operations import utc_timestamp

STRFTIME_MICROSECONDS = '%Y-%m-%dT%H:%M:%SZ'


class StrategyExecution:
    """
    An execution of a strategy.
    """
    current_version = 0
    # The properties in **kwargs that can be null. Note that this is different from the fields that can be null at
    # the database layer
    # No way to reliably get all of the fields of an object so they have to be tracked:
    # https://stackoverflow.com/questions/21945067/how-to-list-all-fields-of-a-class-in-python-and-no-methods
    nullable_fields = [
        # database metadata
        'db_id',
        'db_create_timestamp',
        'db_update_timestamp',
    ]

    required_fields = [
        'version',

        'strategy_id',
        'strategy_execution_id',
        'app_create_timestamp',

        'state',
    ]

    def __init__(self, **kwargs):
        """
        Args:
            **kwargs:
                version: int. Instance schema version
                strategy_id: str. Unique strategy id that specifies the type of strategy being executed.
                strategy_execution_id: str. Unique strategy execution id that specifies the strategy instance.

                app_create_timestamp: float. When the app first created the instance.

                state: Dict. The strategy state. Schemaless to support any type of strategy state. For example:
                    {
                        base: str. Base currency being traded.
                        quote: str. Quote currency being traded.

                        buy_signal_received: bool. Whether a buy signal was received.
                        buy_order_id: str. App id of the buy order.
                        buy_order_status: OrderStatus.

                        sell_signal_received: bool. Whether a sell signal was received.
                        sell_order_id: str. App id of the buy order.
                        sell_order_status: OrderStatus.
                    }


                db_id: int. Id of the entity in the database.
                db_create_timestamp: float. When the entity was created by the database.
                db_update_timestamp: float. When the entity was last updated by the database.
        """
        app_create_timestamp: float = kwargs.get('app_create_timestamp')
        # Instance could either be instantiated for the first time or populated with data from a DTO
        self.app_create_timestamp: float = app_create_timestamp if app_create_timestamp is not None else utc_timestamp()
        self.version: int = kwargs.get('version') if kwargs.get('version') is not None else 0

        self.db_id: int = kwargs.get('db_id')
        self.db_create_timestamp: float = kwargs.get('db_create_timestamp')
        self.db_update_timestamp: float = kwargs.get('db_update_timestamp')

        self.state: Dict = kwargs.get('state', {})

        self.strategy_id = kwargs.get('strategy_id')
        strategy_execution_id = kwargs.get('strategy_execution_id')
        self.strategy_execution_id: str = strategy_execution_id if strategy_execution_id is not None else self.generate_id(
            self.strategy_id)

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

    def generate_id(self, prefix=None) -> str:
        if prefix is None:
            return str(utc_timestamp())
        else:
            return '{0}_{1}'.format(prefix, utc_timestamp())
