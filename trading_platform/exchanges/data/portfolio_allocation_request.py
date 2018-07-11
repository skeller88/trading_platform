class PortfolioAllocationRequest:
    """
    A request for portfolio allocation of a particular currency on a particular exchange. Processed by the
    PortfolioManagerService to allocate initial capital to a strategy instance.
    """
    def __init__(self, exchange_id: int, currency: str):
        self.exchange_id: int = exchange_id
        self.currency: str = currency
        self.id = '{0}_{1}'.format(exchange_id, currency)