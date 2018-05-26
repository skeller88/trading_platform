from trading_platform.exchanges.data import standardizers
from trading_platform.exchanges.data.enums import exchange_ids
from trading_platform.exchanges.data.pair import Pair
from trading_platform.utils.datetime_operations import utc_timestamp


class Ticker:
    """
    Represents ticker data for a given bid currency and quote currency.

    created_at: when entity was created by the database
    event_time: when the entity was created by the exchange
    processing_time: when the arbitrage data was initially received by the application
    updated_at: when entity was updated by the database

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
    current_version = 4

    required_fields = [
        'ask',
        'bid',
        'last',
        'base',
        'quote',
        'exchange_id',
        'processing_time',
        'version'
    ]

    def __init__(self, **kwargs):
        """
        :param ask:
        :param bid:
        :param version:
        :param quote:
        :param db_id:
        :param processing_time:
        :param event_time:
        :param base:
        :param last: last price
        :param exchange:
        """
        self.ask = kwargs.get('ask')
        self.bid = kwargs.get('bid')
        self.last = kwargs.get('last')

        self.base = kwargs.get('base')
        self.quote = kwargs.get('quote')

        self.exchange_id = kwargs.get('exchange_id')
        self.event_time = kwargs.get('event_time')

        self.processing_time = kwargs.get('processing_time') if kwargs.get('processing_time') is not None else utc_timestamp()
        self.db_id = kwargs.get('db_id')
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
        kwargs = {
            'ask': standardizers.bid_or_ask(ticker.get('ask')),
            'bid': standardizers.bid_or_ask(ticker.get('bid')),
            'exchange_id': exchange_id,
            'event_time': ticker.get('timestamp'),
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

            'base',
            'quote',

            'exchange_id',
            'event_time',
            'processing_time',

            'version'
        ]