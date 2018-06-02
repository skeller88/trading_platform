from abc import ABC, abstractmethod


class StrategyFinderServiceAbc(ABC):
    @abstractmethod
    def step(self, **kwargs):
        pass
