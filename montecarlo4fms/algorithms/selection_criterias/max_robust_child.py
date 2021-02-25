from typing import Sequence, Dict

from montecarlo4fms.algorithms.selection_criterias import SelectionCriteria


class MaxRobustChild(SelectionCriteria):
    """
    Select the child with the highest visit count and the highest reward;
    if none exists, then continue searching until an acceptable visit count is achieved.

    Ref.:
        Coulom[2006] - Efficient selectivity and backup operators in Monte-Carlo tree search.
    """

    def best_child(self, state: 'State', children: Sequence['State'], rewards: Dict['State', float], visits: Dict['State', int]) -> 'State':
        raise NotImplementedError
