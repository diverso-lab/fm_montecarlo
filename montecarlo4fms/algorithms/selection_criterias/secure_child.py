from typing import Sequence, Dict

from montecarlo4fms.algorithms.selection_criterias import SelectionCriteria


class SecureChild(SelectionCriteria):
    """Select the child which maximizes a lower conficence bound."""

    def best_child(self, state: 'State', children: Sequence['State'], rewards: Dict['State', float], visits: Dict['State', int]) -> 'State':
        raise NotImplementedError
