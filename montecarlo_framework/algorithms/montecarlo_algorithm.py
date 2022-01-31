from abc import ABC, abstractmethod

from montecarlo_framework.algorithms import Algorithm
from montecarlo_framework.algorithms.stopping_conditions import StoppingCondition
from montecarlo_framework.algorithms.selection_criterias import SelectionCriteria
from montecarlo_framework.models import Node


class MonteCarloAlgorithm(Algorithm):
    """
    Generalization of a MonteCarlo strategy.
    First rollout simulations until a stopping condition is reached,
    then choose the best action (state successor).
    """

    @abstractmethod
    def get_selection_criteria(self) -> SelectionCriteria:
        """Selection criteria for the best child."""
    
    @abstractmethod
    def get_decision_stopping_condition(self) -> StoppingCondition:
        """Stopping condition for choosing each decision in the Monte Carlo algorithm."""

    def choose(self, node: Node) -> Node:
        """Choose the best successor of the state represented by the given node."""
        self.get_decision_stopping_condition().initialize()
        while not self.get_decision_stopping_condition().reached():
            self.do_rollout(node)
            self.get_decision_stopping_condition().update()
        return self.get_selection_criteria().best_child(node)

    @abstractmethod
    def do_rollout(self, node: Node):
        """Apply the Monte Carlo strategy."""

    @abstractmethod
    def get_nof_terminal_states_evaluated(self) -> int:
        """Return the number of terminal states evaluated during simulations for the search."""

    @abstractmethod
    def get_total_nof_simulations(self) -> int:
        """Return the total number of simulations run for the search."""

    @abstractmethod
    def get_total_nof_positive_evaluations(self) -> int:
        """Return the total number of terminal states whose evaluation have been positive (> 0)."""
