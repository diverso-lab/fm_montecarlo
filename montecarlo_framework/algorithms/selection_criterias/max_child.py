from montecarlo_framework.models.search_space import Node
from montecarlo_framework.algorithms.selection_criterias import SelectionCriteria


class MaxChild(SelectionCriteria):
    """Select the child with the highest reward."""

    def score(self, node: Node, rewards: dict[Node, float], visits: dict[Node, int]) -> float:
        """The Q-value (expected reward) of the node."""
        if visits[node] == 0:
            return float("-inf")  # avoid unseen nodes
        return rewards[node] / visits[node]  # average reward

    def best_child(self, node: Node, children: list[Node], rewards: dict[Node, float], visits: dict[Node, int]) -> Node:
        return max(children, key=lambda s: self.score(s, rewards, visits))
