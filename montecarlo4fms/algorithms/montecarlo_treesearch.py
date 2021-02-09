import random
import math
from collections import defaultdict
from typing import List
from montecarlo4fms.algorithms import MonteCarlo
from montecarlo4fms.models import State


class MonteCarloTreeSearch(MonteCarlo):
    """
    Monte Carlo tree search strategy.
    First rollout the MC tree then choose a move."
    """

    def __init__(self, n_simulations: int, exploration_weight: float = 0.5):
        self.n_simulations = n_simulations
        self.exploration_weight = exploration_weight
        self._initialize()

    def _initialize(self):
        self.Q = defaultdict(int)   # total reward of each state
        self.N = defaultdict(int)   # total visit count of each state
        self.children = dict()      # children of each state

    def choose(self, state: State) -> State:
        if state.is_terminal():
            raise RuntimeError(f"Montecarlo choose method called on terminal state {state}")

        if state not in self.children:
            successors = state.find_successors()
            self.children[state] = successors

        if len(self.children[state]) == 1:
            return self.children[state][0]
        else:
            for i in range(self.n_simulations):
                self._do_rollout(state)
            return max(self.children[state], key=self.score)

    def _do_rollout(self, state: State):
        "Make the tree one layer better. (Train for one iteration.)"
        path = self._select(state)
        leaf = path[-1]
        self._expand(leaf)
        reward = self.simulate(leaf)
        self._backpropagate(path, reward)

    def _select(self, state: State) -> List[State]:
        "Find an unexplored descendent of `state`"
        path = [state]
        while state in self.children and self.children[state]:
            # while state is neither explored nor terminal
            unexplored = self.children[state] - self.children.keys()
            if unexplored:
                s = unexplored.pop()
                path.append(s)
                return path
            state = self._select_uct(state)
            path.append(state)
        return path

    def _select_uct(self, state: State) -> State:
        """Select a child of state, balancing exploration & exploitation."""
        log_N_vertex = math.log(self.N[state])

        def uct(s: State) -> float:
            """Upper confidence bound for trees"""
            return self.Q[s] / self.N[s] + self.exploration_weight * math.sqrt(log_N_vertex / self.N[s])

        return max(self.children[state], key=uct)

    def _expand(self, state: State):
        "Update the `children` dict with the children of `state`"
        if not state in self.children:
            self.children[state] = state.find_successors()

    def _backpropagate(self, path, reward):
        "Send the reward back up to the ancestors of the leaf"
        for state in reversed(path):
            self.N[state] += 1
            self.Q[state] += reward

    def simulate(self, state: State) -> int:
        while not state.is_terminal():
            state = state.find_random_successor()
        return state.reward()

    def score(self, state: State) -> float:
        if self.N[state] == 0:
            return float("-inf")              # avoid unseen state
        return self.Q[state] / self.N[state]  # average reward

    def print_MC_values(self):
        if self.Q.keys():
            print(f"MonteCarloTreeSearch values:")
            for s in self.Q.keys():
                print(f"//MC values for state: {s} -> {self.Q[s]}/{self.N[s]} = {self.score(s)}")
