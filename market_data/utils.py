from market_data.pair import Pair


def check_required_fields(instance):
    for field in instance.required_fields:
        if getattr(instance, field) is None:
            raise AttributeError('{0} is missing required field {1}'.format(instance, field))


def get_pair_names(bases, quotes):
    """
    Given a list of bases and quotes, returns all unique possible combinations of those quotes and bases.
    :param bases: ['BTC', 'ETH']
    :param quotes: ['BTC', 'ETH', 'XMR']
    :return: {'BTC_ETH', 'BTC_XMR', 'ETH_XMR', ...}
    """
    pair_names = set()
    for base in bases:
        for quote in quotes:
            pair_names.add(Pair(base=base, quote=quote).name)

    return pair_names