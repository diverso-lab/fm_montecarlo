from typing import Sequence, Dict

from montecarlo4fms.algorithms.selection_criterias import SelectionCriteria


class MaxChild(SelectionCriteria):
    """Select the child with the highest reward."""

    def score(self, s: 'State', rewards: Dict['State', float], visits: Dict['State', int]) -> float:
        """The Q-value (expected reward) of the state."""
        if visits[s] == 0:
            return float("-inf")       # avoid unseen state
        return rewards[s] / visits[s]  # average reward

    def best_child(self, state: 'State', children: Sequence['State'], rewards: Dict['State', float], visits: Dict['State', int]) -> 'State':
        return max(children, key=lambda s: self.score(s, rewards, visits))
