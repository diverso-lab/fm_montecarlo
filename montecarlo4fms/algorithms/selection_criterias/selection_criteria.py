from abc import ABC, abstractmethod
from typing import Sequence, Dict


class SelectionCriteria(ABC):
    """
    Selection criteria for selecting the winning action (best children of a state).
    Four criteria are described in Schadd[2009] based on Chaslot[2008].

    Refs.:
        Schadd[2009] - Monte-Carlo search techniques in the modern board game Thurn and Taxis.
        Chaslot[2009] - Progressive strategies for Monte-Carlo tree search.
    """

    def score(self, s: 'State', rewards: Dict['State', float], visits: Dict['State', int]) -> float:
        """The score of the state"""
        pass

    @abstractmethod
    def best_child(self, state: 'State', children: Sequence['State'], rewards: Dict['State', float], visits: Dict['State', int]) -> 'State':
        """Select the best child of state according to its score."""
        pass
