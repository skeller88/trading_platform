from abc import ABC, abstractmethod


class StrategyExecuterServiceAbc(ABC):
    @abstractmethod
    def step(self, **kwargs):
        pass
