import math

from montecarlo4fms.algorithms import MonteCarloTreeSearch
from montecarlo4fms.models import State


class UCTAlgorithm(MonteCarloTreeSearch):
    """
    Upper confidence bounds for trees (UCT) policy.

    Ref.:
        Gelly[2011] - Monte-Carlo tree search and rapid action value estimation in computer Go
    """

    def __init__(self, stopping_condition: 'StoppingCondition', selection_criteria: 'SelectionCriteria', exploration_weight: float = 0.5):
        super().__init__(stopping_condition, selection_criteria)
        self.exploration_weight = exploration_weight

    def best_child(self, state: State) -> State:
        """Select the best child of state, balancing exploration and exploitation."""
        log_N_vertex = math.log(self.N[state])

        def uct(s: State) -> float:
            """Upper confidence bounds for trees."""
            return self.Q[s] / self.N[s] + self.exploration_weight * math.sqrt(log_N_vertex / self.N[s])

        return max(self.tree[state], key=uct)
