from typing import List

from montecarlo4fms.algorithms import MCTSIterations
from montecarlo4fms.models import State


class MCTSIterationsRandomPolicy(MCTSIterations):
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
        path = [state]
        while state in self.tree and self.tree[state]:  # while state is neither explored nor terminal
            possible_unexplored = state.find_random_successor()
            if not possible_unexplored in self.tree[state] or not possible_unexplored in self.tree:
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
        child = state.find_random_successor()
        if not state in self.tree:
            self.tree[state] = [child]
        else:
            if not child in self.tree[state]:
                self.tree[state] += [child]
