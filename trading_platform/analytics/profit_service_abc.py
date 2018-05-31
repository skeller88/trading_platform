from abc import ABC, abstractmethod


class ProfitServiceAbc(ABC):
    @abstractmethod
    def profit_summary(self, exchange_services, end_tickers):
        pass

