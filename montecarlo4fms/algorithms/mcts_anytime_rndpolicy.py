from typing import List

from montecarlo4fms.algorithms import MCTSAnytime
from montecarlo4fms.models import State


class MCTSAnytimeRandomPolicy(MCTSAnytime):
    """
    This version overrides the selection and expansion functions to avoid expanding all successors of the current state.
    """

    def select(self, state: State) -> List[State]:
        """
        Step 1: Selection.
        Find an expandable/unexplored child node of `state`.
        A node is expandable if it represents a nonterminal state and has unvisited.
        The tree policy is applied recursively until a leaf node is reached.
        Return the list of nodes visited.
        """
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
        """
        Step 2: Expansion.
        Update the tree with the children of 'state'.
        """
        if not self.already_expanded:
            if not state.is_terminal():
                if not state in self.tree:
                    self.tree[state] = [state.find_random_successor()]
                else:
                    child = state.find_random_successor()
                    if not child in self.tree[state]:
                        self.tree[state] += [child]
