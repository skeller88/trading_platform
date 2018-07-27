from trading_platform.exchanges.data import standardizers
from trading_platform.exchanges.data.enums import exchange_ids
from trading_platform.exchanges.data.financial_data import FinancialData
from trading_platform.exchanges.data.pair import Pair
from trading_platform.utils.datetime_operations import utc_timestamp


class Ticker:
    """
    Represents ticker data for a given bid currency and quote currency.

    db_create_timestamp: when entity was created by the database
    exchange_timestamp: when the entity was created by the exchange
    app_create_timestamp: when the arbitrage data was initially received by the application
    db_update_timestamp: when entity was updated by the database

    Application
    - used to determine arbitrage opportunities

    Analytics
    - determine arbitrage opportunities during backtesting
    - build models on what market conditions will lead to the most profitable arbitrage
    - potentially build other trading models on top of the data

    Decimals are always used for financial values because floats have limited precision, and while floats probably will
    have enough precision for the calculations in this app, it's not certain, and that would be a pain to refactor. A satoshi is
    0.00000001 BTC, so add a few digits and you could see how you could potentially run out of significant digits.
    http://effbot.org/pyfaq/why-are-floating-point-calculations-so-inaccurate.htm.

    The timestamps, on the other hand, are represented as floats. Decimal would offer a nanosecond level of precision,
    which is unnecessary: https://mail.python.org/pipermail/python-dev/2012-February/116837.html
    """
    # first ticker version that has volume fields
    first_version_with_volume_fields = 5
    current_version = 5

    # Don't include last because "last" isn't included in the aggregated csv files right now.
    numerical_fields = [
        'ask',
        'bid',
    ]

    required_fields = [
        'ask',
        'bid',
        'last',

        'base',
        'quote',
        'exchange_id',
        'app_create_timestamp',
        'version'
    ]

    nullable_fields = [
        'base_volume',
        'quote_volume',

        'db_id',
        'db_create_timestamp',
        'db_update_timestamp',
        'exchange_timestamp'
    ]

    def __init__(self, **kwargs):
        """
        Args:
            kwargs: Dict
                ask:
                bid:
                version:
                quote:
                db_id:
                app_create_timestamp:
                exchange_timestamp:
                base:
                last: last price
                exchange:
        """
        self.ask = kwargs.get('ask')
        self.bid = kwargs.get('bid')
        self.last = kwargs.get('last')

        self.base_volume = kwargs.get('base_volume')
        self.quote_volume = kwargs.get('quote_volume')

        self.base = kwargs.get('base')
        self.quote = kwargs.get('quote')

        self.exchange_id = kwargs.get('exchange_id')
        self.exchange_timestamp = kwargs.get('exchange_timestamp')

        self.app_create_timestamp = kwargs.get('app_create_timestamp') if kwargs.get('app_create_timestamp') is not None else utc_timestamp()
        self.db_id = kwargs.get('db_id')
        self.db_create_timestamp = kwargs.get('db_create_timestamp')
        self.db_update_timestamp = kwargs.get('db_update_timestamp')
        self.version = kwargs.get('version')

    # https://stackoverflow.com/questions/390250/elegant-ways-to-support-equivalence-equality-in-python-classes
    def __eq__(self, other):
        """Overrides the default implementation"""
        if isinstance(self, other.__class__):
            return self.__dict__ == other.__dict__
        return NotImplemented

    def __hash__(self):
        """Overrides the default implementation"""
        return hash(tuple(sorted(self.__dict__.items())))

    def to_dict(self):
        """
        Returns:

        """
        return {attr: getattr(self, attr) for attr in self.csv_fieldnames()}

    @classmethod
    def from_exchange_data(cls, ticker, exchange_id, version):
        """
        :param ticker:
        :param exchange_id:
        :return: str, Ticker. str is the pair name which is used frequently as the key for the ticker in a dict of
        tickers to be returned from an exchange.fetch_tickers() method.

        Args:
            version:
        """
        if ticker is None:
            return None, None

        pair = Pair.from_exchange_client_string(ticker.get('symbol'))

        if pair is None:
            print('No pair found for ticker data {0}'.format(ticker))
            return None, None

        kwargs = {
            'ask': standardizers.bid_or_ask(ticker.get('ask')),
            'bid': standardizers.bid_or_ask(ticker.get('bid')),

            'base_volume': FinancialData(ticker.get('baseVolume')),
            'quote_volume': FinancialData(ticker.get('quoteVolume')),

            'exchange_id': exchange_id,
            'exchange_timestamp': ticker.get('timestamp'),
            'last': standardizers.last(ticker.get('last')),
            'version': version,

            'base': pair.base,
            'quote': pair.quote
        }

        return pair.name, cls(**kwargs)

    @classmethod
    def from_csv_data(cls, ticker_dict, csv_version):
        if ticker_dict is None:
            return None

        if ticker_dict.get('exchange_id') and len(ticker_dict.get('exchange_id')) != 1:
            # Due to a bug in writing ticker_dict data, the "name" is being written instead of the "id" even when the fieldname
            # is "exchange_id"
            ticker_dict['exchange_id'] = exchange_ids.from_name(ticker_dict.get('exchange_name'))
        elif ticker_dict.get('exchange_name'):
            ticker_dict['exchange_id'] = exchange_ids.from_name(ticker_dict.get('exchange_name'))

        return cls(**ticker_dict)

    @staticmethod
    def classname():
        return 'ticker'

    @staticmethod
    def csv_fieldnames():
        """
        db_id is not included because there's no need for that field yet.
        Returns:

        """
        return [
            'ask',
            'bid',
            'last',

            'base_volume',
            'quote_volume',

            'base',
            'quote',

            'exchange_id',
            'exchange_timestamp',
            'app_create_timestamp',

            'version'
        ]