import random
from collections import defaultdict
from montecarlo4fms.algorithms import MonteCarlo
from montecarlo4fms.models import State

class MonteCarloBasic(MonteCarlo):
    """
    Basic implementation of the MonteCarlo strategy.
    It first runs n simulations, then chooses the best state.
    """

    def __init__(self, n_simulations: int):
        self.n_simulations = n_simulations
        self._initialize()

    def _initialize(self):
        self.Q = defaultdict(int)   # total reward of each state
        self.N = defaultdict(int)   # total visit count of each state

    def choose(self, state: State) -> State:
        if state.is_terminal():
            raise RuntimeError(f"Montecarlo choose method called on terminal state {state}")

        self._initialize()
        successors = state.find_successors()
        if len(successors) == 1:
            return successors[0]
        else:
            for i in range(self.n_simulations):
                s = random.choice(successors)
                reward = self.simulate(s)
                self.Q[s] += reward
                self.N[s] += 1

            return max(self.Q.keys(), key=self.score)

    def simulate(self, state: State) -> int:
        while not state.is_terminal():
            state = state.find_random_successor()
        return state.reward()

    def score(self, state: State) -> float:
        if self.N[state] == 0:
            return float("-inf")              # avoid unseen state
        return self.Q[state] / self.N[state]  # average reward

    def print_MC_values(self):
        for s in self.Q.keys():
            print(f"//MC values for state: {s} -> {self.Q[s]}/{self.N[s]} -> {self.score(s)}")
