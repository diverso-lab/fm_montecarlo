import random
import math
from collections import defaultdict
from typing import List
from montecarlo4fms.algorithms import MonteCarlo
from montecarlo4fms.models import State


class MonteCarloTreeSearch(MonteCarlo):
    """
    Monte Carlo Tree Search (MCTS) strategy.
    It iteratively builds a search tree until some predefined computational budget is reached.
    It uses the UCT algorithm for the policy tree.
    It uses uniform random choices as the default policy for simulations.
    """

    def __init__(self, exploration_weight: float = 0.5):
        self.exploration_weight = exploration_weight
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
        """Choose the best successor of node."""
        #if state.is_terminal():
        #    raise RuntimeError(f"Montecarlo choose method called on terminal state {state}")

        if state not in self.tree:
            return state.find_random_successor()
        return max(self.tree[state], key=self.score)

    def score(self, state: State) -> float:
        """The Q-value (expected reward) of the state."""
        if self.N[state] == 0:
            return float("-inf")              # avoid unseen state
        return self.Q[state] / self.N[state]  # average reward

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

    def best_child(self, state: State) -> State:
        """
        Select the best child of state, balancing exploration and exploitation.
        It uses the Upper confidence bounds for trees (UCT) policy.
        """
        log_N_vertex = math.log(self.N[state])

        def uct(s: State) -> float:
            """Upper confidence bounds for trees."""
            return self.Q[s] / self.N[s] + self.exploration_weight * math.sqrt(log_N_vertex / self.N[s])

        return max(self.tree[state], key=uct)

    def print_MC_values(self, state):
        print(f"MonteCarloTreeSearch values:")
        for s in self.tree[state]:
            print(f"//MC values for state: {[str(f) for f in s.feature_model.get_features()]} -> {self.Q[s]}/{self.N[s]} = {self.score(s)}")
