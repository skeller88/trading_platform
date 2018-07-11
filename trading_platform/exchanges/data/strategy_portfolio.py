from collections import defaultdict
from decimal import Decimal
from typing import List, Dict

from trading_platform.exchanges.data.financial_data import FinancialData


class StrategyPortfolio:
    def __init__(self, exchange_ids: List[int]):
        self.free: Dict[int, defaultdict[str, FinancialData]] = {exchange_id: defaultdict(FinancialData) for exchange_id in
                                                                 exchange_ids}
        self.locked: Dict[int, defaultdict[str, FinancialData]] = {exchange_id: defaultdict(FinancialData) for exchange_id in
                                                                   exchange_ids}
