from abc import ABC, abstractmethod
from montecarlo4fms.models import State


class MonteCarlo(ABC):
    """
    Generalization of a MonteCarlo strategy.
    First rollout simulations, then choose the best action (state).
    """

    def run(self, state: State) -> State:
        """Run the Monte Carlo algorithm. Return the best performing state."""
        while not self.stopping_condition():
            self.do_rollout(state)
        return self.choose(state)

    @abstractmethod
    def do_rollout(self, state: State):
        """Apply the Monte Carlo strategy."""
        pass

    @abstractmethod
    def choose(self, state: State) -> State:
        """Choose the best successor of state."""
        pass

    @abstractmethod
    def stopping_condition(self) -> bool:
        """Return True if some computational budget is reached, False otherwise.
        Typically a time, memory or iteration constraint."""
        pass
