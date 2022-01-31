from abc import ABC, abstractmethod

from montecarlo_framework.models import Problem, Solution
from montecarlo_framework.algorithms.stopping_conditions import StoppingCondition


class Algorithm(ABC):
    """Abstract algorithm that works with a search space of (States, Actions)."""

    @staticmethod
    @abstractmethod
    def get_name() -> str:
        """Name of the algorithm."""

    @abstractmethod
    def get_stopping_condition(self) -> StoppingCondition:
        """Stopping condition of the algorithm to find a solution."""
    
    @abstractmethod
    def initialize(self) -> None:
        """Initialize the internal state of the algorithm.
        
        This method should be called before each run of the algorithm.
        """

    @abstractmethod
    def run(self, problem: Problem) -> Solution:
        """Execute the algorithm.
        
        The algorithm runs from a given state until a terminal state is found or
        until a stopping codition (e.g., time, memory, iterations) is meet.

        It returns the solution.
        """
