import logging
from typing import Dict, List, Optional

from trading_platform.exchanges.data.enums import exchange_ids
from trading_platform.exchanges.data.financial_data import FinancialData, zero, one
from trading_platform.exchanges.data.portfolio import Portfolio
from trading_platform.exchanges.data.portfolio_allocation_request import PortfolioAllocationRequest
from trading_platform.utils.exceptions import PortfolioAllocationException


class TestPortfolioManagerService:
    def test_allocate_portfolio(self):
        pass
