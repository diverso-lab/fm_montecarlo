from typing import List

from montecarlo4fms.algorithms import UCTAlgorithm
from montecarlo4fms.models import State


class UCTRandomExpansion(UCTAlgorithm):
    """
    It expands a random child node instead of all children of a node.
    """

    def select(self, state: State) -> List[State]:
        self.already_expanded = False
        path = [state]
        while state in self.tree and self.tree[state]:  # while state is neither explored nor terminal
            unexplored = self.tree[state] - self.tree.keys()
            if unexplored:  # the node is not fully expanded
                s = unexplored.pop()
                path.append(s)
                return path
            else:
                possible_unexplored = state.find_random_successor()
                if not possible_unexplored in self.tree[state]: # the node is not yet fully expanded
                    self.already_expanded = True
                    self.tree[state] += [possible_unexplored]
                    path.append(possible_unexplored)
                    return path
            state = self.best_child(state)
            path.append(state)
        return path

    def expand(self, state: State):
        if not self.already_expanded:
            if not state.is_terminal():
                if not state in self.tree:
                    self.tree[state] = [state.find_random_successor()]
                else:
                    child = state.find_random_successor()
                    if not child in self.tree[state]:
                        self.tree[state] += [child]
