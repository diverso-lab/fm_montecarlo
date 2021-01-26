from abc import ABC, abstractmethod

class MonteCarlo(ABC):
    """
    Generalization of a MonteCarlo strategy.
    First rollout simulations, then choose a state (e.g., move, configuration).
    """

    @abstractmethod
    def choose(self, state: State) -> State:
        """Choose the best successor of state."""
        pass

    @abstractmethod
    def simulate(self, state: State) -> int:
        """Returns the reward for a random simulation (to completion) from the given state."""
        pass

    @abstractmethod
    def score(self, state: State) -> float:
        """Returns the score of the state taking into account all simulations performed.
        It is normally the average of the rewards for this state."""
        pass
