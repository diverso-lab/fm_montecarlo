import math

from montecarlo4fms.algorithms import UCTAlgorithm
from montecarlo4fms.algorithms.stopping_conditions import StoppingCondition
from montecarlo4fms.algorithms.selection_criterias import SelectionCriteria


class GreedyMCTS(UCTAlgorithm):
    """
    Upper confidence bounds for trees (UCT) policy.

    Ref.:
        Gelly[2011] - Monte-Carlo tree search and rapid action value estimation in computer Go
    """

    def __init__(self, stopping_condition: StoppingCondition, selection_criteria: SelectionCriteria):
        super().__init__(stopping_condition, selection_criteria, 0.0)

    def __str__(self) -> str:
        return f"Greedy MCTS ({str(self.stopping_condition)})"
