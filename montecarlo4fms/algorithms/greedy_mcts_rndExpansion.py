from typing import List

from montecarlo4fms.algorithms import UCTRandomExpansion
from montecarlo4fms.models import State


class GreedyMCTSRandomExpansion(UCTRandomExpansion):
    """
    It expands a random child node instead of all children of a node.
    """
    def __init__(self, stopping_condition: 'StoppingCondition', selection_criteria: 'SelectionCriteria'):
        super().__init__(stopping_condition, selection_criteria, 0.0)

    def __str__(self) -> str:
        return f"Greedy MCTS Rnd Exp ({str(self.stopping_condition)})"
