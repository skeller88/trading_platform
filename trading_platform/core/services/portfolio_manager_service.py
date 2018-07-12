import logging
from typing import Dict, List, Optional

from trading_platform.exchanges.data.enums import exchange_ids
from trading_platform.exchanges.data.financial_data import FinancialData, zero, one
from trading_platform.exchanges.data.portfolio import Portfolio
from trading_platform.exchanges.data.portfolio_allocation_request import PortfolioAllocationRequest
from trading_platform.utils.exceptions import PortfolioAllocationException


class PortfolioManagerService:
    """
    A "portfolio" is defined as a set of amounts of currencies across one or more exchanges. For example,

    Allocate % of portfolio on each exchange to each strategy instance, and keep track of the current portfolio
    allocated to each instance.

    Example usage of the service. Note that the dictionary value for each strategy id key is actually represented
    by a StrategyPortfolio instance. The dictionary is to show the internals of the StrategyPortfolio.free property.

    Start
    binance - 2 BTC
    bittrex - 4 ETH
    portfolios_by_strategy: {
      'free': {'binance': {'BTC': 2}, 'bittrex: {'ETH': 4} }
    }

    receive arbitrage signal for BTC and ETH
    create arbitrage strategy execution instance, "arb_btc_eth_1"
    query portfolio manager for initial capital allocated to a new arbitrage strategy. It's 50% of free balance on each
    exchange.

    Execute
    arb_btc_eth_1 - allocate 50% of each of current free balances - 1 BTC on binance and 2 ETH on bittrex
    portfolios_by_strategy: {
      'arb_btc_eth_1': {'binance': {'ETH': 2}, 'bittrex: {'BTC': 1} }
      'free': {'binance': {'BTC': 1}, 'bittrex: {'ETH': 2} }
    }

    arb_btc_eth_1 - rebalance 1 BTC from binance to bittrex and 2 ETH from bittrex to binance. Note that a strategy
    may attempt to use the allotted balance before the deposit has completed. Waiting until completion is an enchancement
    for later.
    portfolios_by_strategy: {
      'arb_btc_eth_1': {'binance': {'ETH': 2}, 'bittrex: {'BTC': 1} }
      'free': {'binance': {'BTC': 1}, 'bittrex: {'ETH': 2} }
    }

    arb_btc_eth_1 - bittrex - buy 3 ETH, spend 1 BTC.
    portfolios_by_strategy: {
      'arb_btc_eth_1': {'binance': {'ETH': 2}, 'bittrex: {'ETH': 3} }
      'free': {'binance': {'BTC': 1}, 'bittrex: {'ETH': 2} }
    }

    arb_btc_eth_1 - binance - sell 2 ETH, gain 1.2 BTC.
    portfolios_by_strategy: {
      'arb_btc_eth_1': {'binance': {'ETH': 1.2}, 'binance': {'ETH': 3} }
      'free': {'binance': {'BTC': 1}, 'bittrex: {'ETH': 2} }
    }

    receive buy signal for XRP.
    create "nm_xrp_1 execution" instance
    query portfolio manager for initial capital allocated to a new arbitrage strategy. It's 50% of free balance on exchange
    to purchase (binance).
    'nm_xrp_1' - add .5 BTC to portfolio
    portfolios_by_strategy: {
      'arb_btc_eth_1': {'binance': {'ETH': 1.2}, 'binance': {'ETH': 3} }
      'nm_xrp_1': {'binance': {'BTC': .5 } }
      'free': {'binance': {'BTC': .5}, 'bittrex: {'ETH': 2} }
    }

    Execute

    nm_xrp_1 - bittrex - buy 5000 XRP, spend .5 BTC
    portfolios_by_strategy: {
      'arb_btc_eth_1': {'binance': {'ETH': 1.2}, 'binance': {'ETH': 3} }
      'nm_xrp_1': {'bittrex': {'XRP': 5000 } }
      'free': {'binance': {'BTC': .5}, 'bittrex: {'ETH': 2} }
    }

    nm_xrp_1 - bittrex - sell 5000 XRP, gain 1.5 BTC
    portfolios_by_strategy: {
      'arb_btc_eth_1': {'binance': {'ETH': 1.2}, 'binance': {'ETH': 3} }
      'nm_xrp_1': {'bittrex': {'BTC': 1.5 } }
      'free': {'binance': {'BTC': .5}, 'bittrex: {'ETH': 2} }
    }

    nm_xrp_1 - bittrex - release 1.5 BTC into "free" portfolio and end strategy.
    portfolios_by_strategy: {
      'arb_btc_eth_1': {'binance': {'ETH': 1.2}, 'binance': {'ETH': 3} }
      'nm_xrp_1': {'bittrex': {'BTC': 1.5 } }
      'free': {'binance': {'BTC': 2}, 'bittrex: {'ETH': 2} }
    }
    """

    # balances that are free to be allocated into a portfolio
    free_balances = 'free_balances'

    def __init__(self, logger: logging.Logger,
                 portfolios_by_strategy: Dict[str, Portfolio],
                 portfolio_percent_allocation_rules: Dict[int, FinancialData]):
        """
        Args:
            portfolios_by_strategy: Dict[str, StrategyPortfolio]. The initial portfolios by strategy
                id. A portfolio consists of the balances of the currencies allocated to the strategy on each exchange.
            Example: {
                'nm_1': <StrategyPortfolio instance>
            }


            portfolio_percent_allocation_rules" Dict[int, Decimal]. The % of available portfolio per exchange and per
            currency requested that will be allocated to a new strategy instance, given its strategy type.
            Example: {
                StrategyId.nm: .5
                StrategyId.arb: .5
            }
        """
        self.logger = logger
        self.portfolios_by_strategy: Dict[str, Portfolio] = portfolios_by_strategy
        self.portfolio_percent_allocation_rules: Dict[int, FinancialData] = portfolio_percent_allocation_rules

    def allocate_portfolio(self, strategy_type: str, strategy_id: str,
                           portfolio_allocation_requests: List[PortfolioAllocationRequest]) -> Optional[
        Portfolio]:
        """
        Args:
            strategy_type:
            strategy_id:
            portfolio_allocation_requests: List

        Returns:
        """
        # check for duplicates
        if len(portfolio_allocation_requests) != len(set(portfolio_allocation_requests)):
            raise PortfolioAllocationException('Duplicate PortfolioAllocationRequest found')

        percent_allocation: FinancialData = self.portfolio_percent_allocation_rules.get(strategy_type)

        if percent_allocation is None:
            raise PortfolioAllocationException('percent_allocation for strategy_type {0} not found'.format(strategy_type))
        elif not FinancialData(.01) <= percent_allocation <= one:
            raise PortfolioAllocationException('percent_allocation {0} not in [.1, 1]'.format(percent_allocation))

        portfolio = Portfolio(exchange_ids.all_ids)
        for request in portfolio_allocation_requests:
            currency_to_allocate: FinancialData = percent_allocation * self.portfolios_by_strategy[self.free_balances].free[
                request.exchange_id].get(request.currency)
            if currency_to_allocate == zero:
                self.logger.info('insufficient funds for portfolio_allocation_request for strategy_type {0}, '
                                 'strategy_id {1}, exchange_id {0}, currency {1}'.format(strategy_type, strategy_id,
                                                                                         request.exchange_id,
                                                                                         request.currency))
                return None

            portfolio.free[request.exchange_id][request.currency] = currency_to_allocate

        self.portfolios_by_strategy[strategy_id] = portfolio
        return portfolio

    def get_portfolio(self, strategy_id: str) -> Portfolio:
        return self.portfolios_by_strategy.get(strategy_id)

    def update_portfolio(self, strategy_id: str, portfolio: Portfolio):
        self.portfolios_by_strategy[strategy_id] = portfolio

    def remove_portfolio(self, strategy_id: str):
        del self.portfolios_by_strategy[strategy_id]
