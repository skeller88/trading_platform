import logging
from collections import defaultdict
from decimal import Decimal
from typing import Dict, List, Optional

from trading_platform.exchanges.data.enums import exchange_ids
from trading_platform.exchanges.data.enums.strategy_type import StrategyType
from trading_platform.exchanges.data.financial_data import FinancialData, zero
from trading_platform.exchanges.data.portfolio_allocation_request import PortfolioAllocationRequest
from trading_platform.exchanges.data.strategy_portfolio import StrategyPortfolio


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
    arb_btc_eth_1 - allocate 50% of each of current free balances - 1 BTC on binance and 4 ETH on bittrex
    portfolios_by_strategy: {
      'arb_btc_eth_1': {'binance': {'BTC': 1}, 'bittrex: {'ETH': 2} }
      'free': {'binance': {'BTC': 1}, 'bittrex: {'ETH': 2} }
    }

    arb_btc_eth_1 - rebalance 1 BTC from binance to bittrex and 1 ETH from bittrex to binance. Note that a strategy
    may attempt to use the alloted balance before the deposit has completed. Waiting until completion is an enchancement
    for later
    portfolios_by_strategy: {
      'arb_btc_eth_1': {'binance': {'BTC': 1}, 'bittrex: {'ETH': 2} }
      'free': {'binance': {'BTC': 1}, 'bittrex: {'ETH': 2} }
    }

    arb_btc_eth_1 - BTC buy order for ETH on bittrex is completed at a price of 3 ETH per BTC.
    portfolios_by_strategy: {
      'arb_btc_eth_1': {'binance': {'ETH': 2}, 'bittrex: {'ETH': 3} }
      'free': {'binance': {'BTC': 1}, 'bittrex: {'ETH': 2} }
    }

    arb_btc_eth_1 - ETH sell order for BTC on binance is completed at a sell price of 1.1 BTC per ETH
    portfolios_by_strategy: {
      'arb_btc_eth_1': {'binance': {'BTC': 1.1}, 'bittrex: {'ETH': 3} }
      'free': {'binance': {'BTC': 1}, 'bittrex: {'ETH': 2} }
    }

    receive buy signal for XRP. Execute buy order on binance.
    create "nm_xrp_1 execution" instance
    query portfolio manager for initial capital allocated to a new arbitrage strategy. It's 50% of free balance on exchange
    to purchase.
    portfolios_by_strategy: {
      'arb_btc_eth_1': {'binance': {'BTC': 1.1}, 'bittrex: {'ETH': 3} }
      'nm_xrp_1': {'binance': {'BTC': .5 } }
      'free': {'binance': {'BTC': .5}, 'bittrex: {'ETH': 2} }
    }

    Execute

    nm_xrp_1 - buy XRP at 5000 XRP/BTC - remove .5 BTC on bittrex, allocate 5000 XRP on bittrex
    portfolios_by_strategy: {
      'arb_btc_eth_1': {'bittrex': {'ETH': 3}, 'binance: {'BTC': 1.1} },
      'nm_xrp_1': {'bittrex': {'XRP': 5000 } }
      'free': {'binance': {'BTC': .5}, 'bittrex: {'ETH': 2} }
    }
    nm_xrp_1 - sell 5000 XRP for 1.5 BTC - end strategy - remove 5000 XRP on bittrex
    portfolios_by_strategy: {
      'arb_btc_eth_1': {'bittrex': {'ETH': 3}, 'binance: {'BTC': 1.1} },
      'free': {'binance': {'BTC': 2}, 'bittrex: {'ETH': 2} }
    }
    """
    default_portfolio_percent_allocation_rules: Dict[str, FinancialData] = {
        StrategyType.arb: 0.5,
        StrategyType.nm: 0.5
    }

    # balances that are free to be allocated into a portfolio
    free_balances = 'free_balances'

    def __init__(self, logger: logging.Logger,
                 portfolios_by_strategy: Dict[str, StrategyPortfolio],
                 portfolio_percent_allocation_rules: Dict[
                     int, FinancialData] = default_portfolio_percent_allocation_rules):
        """
        Args:
            portfolios_by_strategy: Dict[str, StrategyPortfolio]. The initial portfolios by strategy
                id. A portfolio consists of the balances of the currencies allocated to the strategy on each exchange.
            Example: {
                'nm_1': <StrategyPortfolio instance>
            }


            portfolio_percent_allocation_rules" Dict[int, FinancialData]. The % of available portfolio per exchange and per
            currency requested that will be allocated to a new strategy instance, given its strategy type.
            Example: {
                StrategyId.nm: .5
                StrategyId.arb: .5
            }
        """
        self.logger = logger
        self.portfolios_by_strategy: Dict[str, StrategyPortfolio] = portfolios_by_strategy
        self.portfolio_percent_allocation_rules: Dict[int, FinancialData] = portfolio_percent_allocation_rules

    def create_strategy_portfolio(self, strategy_type: int, strategy_id: str,
                                  portfolio_allocation_requests: List[PortfolioAllocationRequest]) -> Optional[
        StrategyPortfolio]:
        """
        Args:
            strategy_type:
            strategy_id:
            portfolio_allocation_requests: List

        Returns:
        """
        # check for duplicates
        seen = set()
        for request in portfolio_allocation_requests:
            if request.id not in seen:
                seen.add(request.id)
            else:
                raise Exception(
                    'Duplicate PortfolioAllocationRequest found for exchange_id {0} and currency {1}'.format(request.id,
                                                                                                             request.currency))

        percent_allocation: FinancialData = self.portfolio_percent_allocation_rules.get(strategy_type)

        if percent_allocation is None:
            raise Exception('strategy_type {0} not found'.format(strategy_type))

        strategy_portfolio = StrategyPortfolio(exchange_ids.all_ids)
        for request in portfolio_allocation_requests:
            currency_to_allocate: FinancialData = percent_allocation * self.portfolios_by_strategy[self.free_balances][
                request.exchange_id].get(request.currency)
            if currency_to_allocate == zero:
                self.logger.info('insufficient funds for portfolio_allocation_request for strategy_type {0}, '
                                 'strategy_id {1}, exchange_id {0}, currency {1}'.format(strategy_type, strategy_id,
                                                                                         request.exchange_id,
                                                                                         request.currency))
                return None

            strategy_portfolio.free[request.exchange_id][request.currency] = currency_to_allocate

        self.portfolios_by_strategy[strategy_id] = strategy_portfolio
        return strategy_portfolio

    def get_strategy_portfolio(self, strategy_id: str) -> StrategyPortfolio:
        return self.portfolios_by_strategy.get(strategy_id)

    def update_strategy_portfolio(self, strategy_id: str, strategy_portfolio: StrategyPortfolio):
        self.portfolios_by_strategy[strategy_id] = strategy_portfolio

    def remove_strategy_portfolio(self, strategy_id: str):
        del self.portfolios_by_strategy[strategy_id]
