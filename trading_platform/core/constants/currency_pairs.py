"""
Pairs to consider for arbitraging. This constant is needed because not all exchanges fetch all orders. Some exchanges
like Binance only fetch orders for a given pair, and we don't want to query all of the pairs.
"""
from trading_platform.exchanges.data.pair import Pair
from trading_platform.exchanges.data.utils import get_pair_names

BASES = ['BTC', 'ETH', 'USDT', 'USD']

# 3 minutes
MAX_ORDER_TIME_SECONDS = 60 * 3
QUOTES = BASES.copy()
# https://itsblockchain.com/top-25-crypto-coins-to-buy-in-2018/
#
QUOTES.extend([
    'ADA',
    'ADX',
    'ARDR',
    'ARK',
    'BAT',
    'BCH',
    'BTC',
    'BTS',
    'CVC',
    'DASH',
    'DGB',
    'EOS',
    'ETC',
    'ETH',
    'GNT',
    'ICX',
    'IOTA',
    'KNC',
    'LSK',
    'LTC',
    'NANO',
    'NEO',
    'OMG',
    'PIVX',
    'POWR',
    'QTUM',
    'STEEM',
    'STRAT',
    'TRX',
    'WAVES',
    'VTC',
    'XLM',
    'XMR',
    'XRP',
    'ZEC'])


def get_pairs(bases, quotes):
    """
    Given a list of bases and quotes, returns all unique possible combinations of those quotes and bases.
    :param bases: ['BTC', 'ETH']
    :param quotes: ['BTC', 'ETH', 'XMR']
    :return: {'BTC_ETH', 'BTC_XMR', 'ETH_XMR', ...}
    """
    pairs = set()
    for base in bases:
        for quote in quotes:
            pairs.add(Pair(base=base, quote=quote))

    return pairs


def get_kaiko_pair_names(bases, quotes):
    """
    Given a list of bases and quotes, returns all unique possible combinations of those quotes and bases.
    :param bases: ['BTC', 'ETH']
    :param quotes: ['BTC', 'ETH', 'XMR']
    :return: {'BTC_ETH', 'BTC_XMR', 'ETH_XMR', ...}
    """
    pair_names = set()
    for base in bases:
        for quote in quotes:
            pair_names.add(Pair(base=base, quote=quote).kaiko_name)

    return pair_names


currency_pairs_list = get_pairs(BASES, QUOTES)
currency_pair_names_list = get_pair_names(BASES, QUOTES)
kaiko_pair_names_list = get_kaiko_pair_names(BASES, QUOTES)
