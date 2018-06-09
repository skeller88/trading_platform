from abc import ABC, abstractmethod


class StrategyExecuterServiceAbc(ABC):
    """
    Handles the execution of a strategy. A strategy can span the lifetime of a single process, or multiple
    processes.
    """
    @abstractmethod
    def refresh_state(self, **kwargs):
        """
        Refresh the exchange and app database state. Can be invoked as part of step(), or pre-emptively
        before step is called.
        Args:
            **kwargs:

        Returns:

        """
        pass

    @abstractmethod
    def step(self, **kwargs):
        """
        Should be idempotent in that a single strategy execution should produce the same exchange and database
        state regardless of how many times it's called.
        Args:
            **kwargs:

        Returns:

        """
        pass
