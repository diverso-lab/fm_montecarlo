from collections.abc import Sequence

from montecarlo4fms.models import State 
from montecarlo4fms.algorithms.selection_criterias import SelectionCriteria


class MaxChild(SelectionCriteria):
    """Select the child with the highest reward."""

    def score(self, s: State, rewards: dict[State, float], visits: dict[State, int]) -> float:
        """The Q-value (expected reward) of the state."""
        if visits[s] == 0:
            return float("-inf")       # avoid unseen state
        return rewards[s] / visits[s]  # average reward

    def best_child(self, state: State, children: Sequence[State], rewards: dict[State, float], visits: dict[State, int]) -> State:
        return max(children, key=lambda s: self.score(s, rewards, visits))
