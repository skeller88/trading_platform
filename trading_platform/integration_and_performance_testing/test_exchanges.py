from typing import Dict, List

import pytest
from nose.tools import eq_

from trading_platform.exchanges.data.balance import Balance
from trading_platform.exchanges.data.enums import exchange_ids
from trading_platform.exchanges.data.financial_data import zero
from trading_platform.exchanges.data.ticker import Ticker
from trading_platform.exchanges.live import live_subclasses


@pytest.fixture(scope='module')
def exchanges_by_id():
    all_live = live_subclasses.instantiate(subclasses=live_subclasses.all_live())
    del all_live[exchange_ids.gdax]
    return all_live


class TestExchanges:
    @pytest.mark.parametrize('exchange', exchanges_by_id().values(),
                             ids=lambda exchange: 'test_fetch_balances_{0}'.format(exchange.exchange_name))
    def test_fetch_balances(self, exchange):
        """
        Exchange actions that hit a private endpoint and require an API secret should succeed.
        Args:
            exchange:

        Returns:

        """
        print(exchange.exchange_id)
        balances: Dict[str, Balance] = exchange.fetch_balances()
        assert (balances is not None)
        balance: Balance = exchange.get_balance('nonexistent_coin')
        eq_(balance.free, zero)

    @pytest.mark.parametrize('exchange', exchanges_by_id().values(),
                             ids=lambda exchange: 'test_fetch_tickers_{0}'.format(exchange.exchange_name))
    def test_fetch_tickers(self, exchange):
        """
        Exchange actions that hit a public endpoint should succeed.
        Args:
            exchange:

        Returns:

        """
        tickers: List[Ticker] = exchange.fetch_latest_tickers()
        assert (tickers is not None)
        assert (len(tickers) > 6)
