from abc import ABC, abstractmethod
from montecarlo4fms.models import State


class MonteCarlo(ABC):
    """
    Generalization of a MonteCarlo strategy.
    First rollout simulations until a stopping condition is reached,
    then choose the best action (state successor).
    """

    @abstractmethod
    def __init__(self, stopping_condition: 'StoppingCondition', selection_criteria: 'SelectionCriteria'):
        self.stopping_condition = stopping_condition
        self.selection_criteria = selection_criteria

    def run(self, state: State) -> State:
        """Run the Monte Carlo algorithm. Return the best performing state."""
        self.stopping_condition.initialize()
        while not self.stopping_condition.reached():
            self.do_rollout(state)
            self.stopping_condition.update()
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
    def score(self, state: State) -> float:
        """The score of the state"""
        pass
