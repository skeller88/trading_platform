import re

alphanumeric_set = '[A-Za-z0-9]'


class Pair:
    """
    Represents a currency pair. Base is the base currency, usually BTC, USD, or USDT. Quote is the quote currency, aka
    the currency that is being traded.
    """
    def __init__(self, base, quote):
        self.base = base
        # ccxt separates the base and quote with a "/", which I'm not as much of a fan of as that character sometimes
        # requires escaping.
        self.name_for_exchange_clients = '{0}/{1}'.format(quote, base)
        self.name = '{0}_{1}'.format(quote, base)
        self.kaiko_name = '{0}{1}'.format(quote, base)
        self.quote = quote

    @classmethod
    def from_exchange_client_string(cls, pair_string):
        """
        Args:
            pair_string str: Example, 'BTC/USDT'

        Returns:

        """
        quote, base = cls.from_string('/', pair_string)
        return cls(quote=quote, base=base)

    @classmethod
    def from_dto_string(cls, pair_string):
        pair_string = pair_string.rstrip()
        quote, base = cls.from_string('_', pair_string)
        return cls(quote=quote, base=base)

    @staticmethod
    def from_string(separator_char, pair_string):
        match_str = '({0}*){1}({2}*)'.format(alphanumeric_set, separator_char, alphanumeric_set)
        match = re.match(match_str, pair_string)

        if match is None:
            return None, None


        base = match.group(2)
        quote = match.group(1)

        # ccxt usually converts BCC to BCH for you, but not always
        if quote == 'BCC':
            quote = 'BCH'

        return quote, base

    @staticmethod
    def name_for_base_and_quote(base, quote):
        """
        Return pair name when no Pair needs to be instantiated.

        Args:
            base:
            quote:

        Returns:

        """
        return '{0}_{1}'.format(quote, base)