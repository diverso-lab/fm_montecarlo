import random
from collections import defaultdict
from montecarlo4fms.algorithms import MonteCarlo
from montecarlo4fms.models import State


class MonteCarloBasic(MonteCarlo):
    """
    Basic implementation of the MonteCarlo strategy.
    It first runs n simulations, then chooses the best state.
    """

    def __init__(self):
        self._initialize()

    def _initialize(self):
        self.Q = defaultdict(int)   # total reward of each state
        self.N = defaultdict(int)   # total visit count of each state

    def run(self, state: State) -> State:
        """Run the Monte Carlo algorithm.
        It performs simulations until some predefined computational budget is reached.
        Return the best performing state.
        """
        self._initialize()
        while not stopping_condition():
            self.do_rollout(state)
        return self.choose(state)

    def do_rollout(self, state: State):
        """Perform a simulation and store the statistics."""
        child = state.find_random_successor()
        reward = self.simulate(child)
        self.Q[child] += reward
        self.N[child] += 1

    def choose(self, state: State) -> State:
        """Choose the best successor of node."""
        #if state.is_terminal():
        #    raise RuntimeError(f"Montecarlo choose method called on terminal state {state}")
        return max(self.Q.keys(), key=self.score)

    def simulate(self, state: State) -> float:
        """
        A simulation is rolled out using uniform random choices.
        Return the simulation's reward (i.e., reward of the terminal state).
        """
        while not state.is_terminal():
            state = state.find_random_successor()
        return state.reward()

    def score(self, state: State) -> float:
        if self.N[state] == 0:
            return float("-inf")              # avoid unseen state
        return self.Q[state] / self.N[state]  # average reward

    def print_MC_values(self):
        for s in self.Q.keys():
            print(f"//MC values for state: {[str(f) for f in s.feature_model.get_features()]} -> {self.Q[s]}/{self.N[s]} = {self.score(s)}")
