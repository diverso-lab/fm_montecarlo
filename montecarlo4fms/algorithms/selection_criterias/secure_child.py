from collections.abc import Sequence

from montecarlo4fms.models import State 
from montecarlo4fms.algorithms.selection_criterias import SelectionCriteria


class SecureChild(SelectionCriteria):
    """Select the child which maximizes a lower confidence bound."""

    def best_child(self, state: State, children: Sequence[State], rewards: dict[State, float], visits: dict[State, int]) -> State:
        raise NotImplementedError
