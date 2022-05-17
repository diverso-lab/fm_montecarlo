import math

from montecarlo_framework.models import Problem, Node, Solution
from montecarlo_framework.algorithms import UCTMCTS
from montecarlo_framework.algorithms.stopping_conditions import StoppingCondition
from montecarlo_framework.algorithms.selection_criterias import SelectionCriteria

from montecarlo_framework.utils.montecarlo_stats import MonteCarloStats
from montecarlo_framework.utils.algorithm_stats import AlgorithmStats
from montecarlo_framework.utils.algorithm_logger import get_logger


class GreedyMCTS(UCTMCTS):
    """
    Upper confidence bounds for trees (UCT) policy.
    Ref.:
        Gelly[2011] - Monte-Carlo tree search and rapid action value estimation in computer Go
    """

    @staticmethod
    def get_name() -> str:
        return 'Greedy MCTS'

    def __init__(self, 
                 stopping_condition: StoppingCondition, 
                 selection_criteria: SelectionCriteria, 
                 decision_stopping_condition: StoppingCondition):
        super().__init__(stopping_condition, selection_criteria, decision_stopping_condition, exploration_weight=0.0)

    def __str__(self) -> str:
        return f"Greedy MCTS ({str(self.stopping_condition)})"

    #@MonteCarloStats('greedy_mcts_steps', logger=get_logger('greedy_mcts_steps'))
    def choose(self, node: Node) -> Node:
        return super().choose(node)

    @AlgorithmStats('GreedyMCTS', logger=None)
    def run(self, problem: Problem) -> Solution:
        return super().run(problem)