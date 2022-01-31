from abc import ABC, abstractmethod

from montecarlo_framework.models.search_space import Node


class SelectionCriteria(ABC):
    """
    Selection criteria for selecting the winning action (best children of a node).
    Four criteria are described in Schadd[2009] based on Chaslot[2008].

    Refs.:
        Schadd[2009] - Monte-Carlo search techniques in the modern board game Thurn and Taxis.
        Chaslot[2009] - Progressive strategies for Monte-Carlo tree search.
    """

    @abstractmethod
    def score(self, node: Node, rewards: dict[Node, float], visits: dict[Node, int]) -> float:
        """The score of the state represented by the given node."""

    @abstractmethod
    def best_child(self, node: Node, children: list[Node], rewards: dict[Node, float], visits: dict[Node, int]) -> Node:
        """Select the best child of state represented by the given node according to its score."""
