import math

from montecarlo_framework.models import Problem, Node, Solution
from montecarlo_framework.algorithms import MonteCarloTreeSearch
from montecarlo_framework.algorithms.stopping_conditions import StoppingCondition
from montecarlo_framework.algorithms.selection_criterias import SelectionCriteria

from montecarlo_framework.utils.montecarlo_stats import MonteCarloStats
from montecarlo_framework.utils.algorithm_stats import AlgorithmStats
from montecarlo_framework.utils.algorithm_logger import get_logger


class UCTMCTS(MonteCarloTreeSearch):
    """
    Upper confidence bounds for trees (UCT) policy.
    Ref.:
        Gelly[2011] - Monte-Carlo tree search and rapid action value estimation in computer Go
    """

    @staticmethod
    def get_name() -> str:
        return 'UCT MCTS'

    def __init__(self, 
                 stopping_condition: StoppingCondition, 
                 selection_criteria: SelectionCriteria, 
                 decision_stopping_condition: StoppingCondition, 
                 exploration_weight: float = 0.5):
        super().__init__(stopping_condition, selection_criteria, decision_stopping_condition)
        self.exploration_weight = exploration_weight

    def best_child(self, node: Node) -> Node:
        """Select the best child of state, balancing exploration and exploitation."""
        log_N_vertex = math.log(self.N[node])

        def uct(n: Node) -> float:
            """Upper confidence bounds for trees."""
            return self.Q[n] / self.N[n] + self.exploration_weight * math.sqrt(log_N_vertex / self.N[n])

        return max(self.tree[node], key=uct)

    def __str__(self) -> str:
        return f"UCT Algorithm ({str(self.stopping_condition)}, ew={self.exploration_weight})"

    #@MonteCarloStats('uct_mcts_steps', logger=get_logger('uct_mcts_steps'))
    def choose(self, node: Node) -> Node:
        return super().choose(node)

    @AlgorithmStats('UCTMCTS', logger=None)
    def run(self, problem: Problem) -> Solution:
        return super().run(problem)