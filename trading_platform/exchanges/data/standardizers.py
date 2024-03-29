"""
Have to do a few conversions of pair names to a common format, so that arbitrage opportunities can be explored.
"""

from trading_platform.exchanges.data.financial_data import FinancialData


def bid_or_ask(value):
    return FinancialData(value) if value is not None else None


def last(price):
    """
    TODO - which exchange requires this method?
    :param price:
    :param exchange:
    :return: float
    """
    return FinancialData(str(price).replace(',', ''))


def currency(currency):
    """
    Certain exchanges use BCH in the ticker name, others use BCC. ccxt library always uses BCC, so convert
    BCH to BCC.
    Args:
        currency strt:

    Returns:

    """
    if currency in ['BCH', 'BCH/BCC']:
        return 'BCC'

    if currency == 'NANO/XRB':
        return 'NANO'

    if currency == 'RVR/VOX':
        return 'RVR'

    return currency