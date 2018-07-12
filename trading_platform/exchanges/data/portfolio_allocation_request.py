class PortfolioAllocationRequest:
    """
    A request for portfolio allocation of a particular currency on a particular exchange. Processed by the
    PortfolioManagerService to allocate initial capital to a strategy instance.
    """
    def __init__(self, exchange_id: int, currency: str):
        self.exchange_id: int = exchange_id
        self.currency: str = currency

    def __hash__(self):
        """Overrides the default implementation"""
        return hash(tuple(sorted(self.__dict__.items())))
