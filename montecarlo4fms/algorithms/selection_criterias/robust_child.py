from collections.abc import Sequence

from montecarlo4fms.models import State 
from montecarlo4fms.algorithms.selection_criterias import SelectionCriteria


class RobustChild(SelectionCriteria):
    """Select the most visited child."""

    def score(self, s: State, rewards: dict[State, float], visits: dict[State, int]) -> float:
        """The visit count of the state."""
        return visits[s]
         
    def best_child(self, state: State, children: Sequence[State], rewards: dict[State, float], visits: dict[State, int]) -> State:
        return max(children, key=lambda s: self.score(s, rewards, visits))
