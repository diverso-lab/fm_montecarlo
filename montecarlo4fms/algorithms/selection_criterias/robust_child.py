from typing import Sequence, Dict

from montecarlo4fms.algorithms.selection_criterias import SelectionCriteria


class RobustChild(SelectionCriteria):
    """Select the most visited child."""

    def score(self, s: 'State', rewards: Dict['State', float], visits: Dict['State', int]) -> float:
        """The visit count of the state."""
        return visits[s]
         
    def best_child(self, state: 'State', children: Sequence['State'], rewards: Dict['State', float], visits: Dict['State', int]) -> 'State':
        return max(children, key=lambda s: self.score(s, rewards, visits))
