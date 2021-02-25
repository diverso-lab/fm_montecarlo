from abc import abstractmethod
from collections import defaultdict
from typing import List

from montecarlo4fms.algorithms import MonteCarlo
from montecarlo4fms.models import State


class MonteCarloTreeSearch(MonteCarlo):
    """
    Monte Carlo Tree Search (MCTS) strategy.
    A search tree is built in an incremental and assymetric manner.
    For each iteration of the algorithm, a tree policy is used to find the most urgent node of the current tree.
    It uses uniform random choices as the default policy for simulations.
    """

    def __init__(self, stopping_condition: 'StoppingCondition', selection_criteria: 'SelectionCriteria'):
        super().__init__(stopping_condition, selection_criteria)
        self.Q = defaultdict(int)   # total reward of each state
        self.N = defaultdict(int)   # total visit count of each state
        self.tree = dict()          # the MC tree as a dict of state -> children

    def do_rollout(self, state: State):
        """Make the search tree one layer better (train for one iteration)."""
        path = self.select(state)
        leaf = path[-1]
        self.expand(leaf)
        reward = self.simulate(leaf)
        self.backpropagate(path, reward)

    def choose(self, state: State) -> State:
        if state not in self.tree:
            return state.find_random_successor()
        return self.selection_criteria.best_child(state, self.tree[state], self.Q, self.N)

    def score(self, state: State) -> float:
        return self.selection_criteria.score(state, self.Q, self.N)

    def select(self, state: State) -> List[State]:
        """
        Step 1: Selection.
        Find an expandable/unexplored child node of `state`.
        A node is expandable if it represents a nonterminal state and has unvisited.
        The tree policy is applied recursively until a leaf node is reached.
        Return the list of nodes visited.
        """
        path = [state]
        while state in self.tree and self.tree[state]:  # while state is neither explored nor terminal (if the node has children in the tree means that is not terminal)
            unexplored = self.tree[state] - self.tree.keys()
            if unexplored:  # the node is not fully expanded
                s = unexplored.pop()
                path.append(s)
                return path
            state = self.best_child(state)
            path.append(state)
        return path

    @abstractmethod
    def best_child(self, state: State) -> State:
        """Select the best child of state in the search tree according to a policy tree."""
        pass

    def expand(self, state: State):
        """
        Step 2: Expansion.
        Update the tree with the children of 'state'.
        """
        if not state in self.tree:
            self.tree[state] = state.find_successors()

    def simulate(self, state: State) -> float:
        """
        Step 3. Simulation.
        A simulation is rolled out using the default policy (uniform random choices).
        Return the simulation's reward (i.e., reward of the terminal state).
        """
        while not state.is_terminal():
            state = state.find_random_successor()
        return state.reward()

    def backpropagate(self, path, reward):
        """
        Step 4. Backpropagation.
        Send the reward back up to the visited nodes in the tree.
        """
        for state in reversed(path):
            self.N[state] += 1
            self.Q[state] += reward

    def print_MC_values(self, state):
        print(f"MonteCarloTreeSearch values:")
        for s in self.tree[state]:
            print(f"//MC values for state: {[str(f) for f in s.feature_model.get_features()]} -> {self.Q[s]}/{self.N[s]} = {self.score(s)}")
