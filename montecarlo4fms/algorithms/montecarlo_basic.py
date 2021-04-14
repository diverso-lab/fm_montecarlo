import random
from collections import defaultdict

from montecarlo4fms.algorithms import MonteCarlo
from montecarlo4fms.models import State


class MonteCarloBasic(MonteCarlo):
    """
    Basic implementation of the MonteCarlo strategy.
    It performs a default policiy for simulations, where uniform random selection are made.
    The chooses the best state according to a criteria.
    """

    def __init__(self, stopping_condition: 'StoppingCondition', selection_criteria: 'SelectionCriteria'):
        super().__init__(stopping_condition, selection_criteria)
        self.initialize()
        self.states_evaluated = dict()         # terminal state -> reward value
        self.terminal_nodes_visits = 0
        self.nof_reward_function_calls = 0
        self.n_evaluations = 0                  # for stats
        self.n_positive_evaluations = 0          # positive rewards # for stats

    def initialize(self):
        super().initialize()
        self.Q = defaultdict(int)   # total reward of each state
        self.N = defaultdict(int)   # total visit count of each state

    def run(self, state: State) -> State:
        """Run the Monte Carlo algorithm.
        It performs simulations until some predefined computational budget is reached.
        Return the best performing state.
        """
        self.initialize()
        return super().run(state)

    def do_rollout(self, state: State):
        """Perform a simulation and store the statistics."""
        child = state.find_random_successor()
        reward = self.simulate(child)
        self.Q[child] += reward
        self.N[child] += 1

    def choose(self, state: State) -> State:
        return self.selection_criteria.best_child(state, self.Q.keys(), self.Q, self.N)

    def score(self, state: State) -> float:
        return self.selection_criteria.score(state, self.Q, self.N)

    def simulate(self, state: State) -> float:
        """
        A simulation is rolled out using uniform random choices.
        Return the simulation's reward (i.e., reward of the terminal state).
        """
        while not state.is_terminal():
            state = state.find_random_successor()
        z = state.reward()
        if state not in self.states_evaluated:
            self.states_evaluated[state] = z
            self.n_evaluations += 1
            if z > 0:
                self.n_positive_evaluations += 1
        self.nof_reward_function_calls += 1
        self.terminal_nodes_visits += 1
        return z

    def print_MC_values(self, state: State):
        for s in self.Q.keys():
            print(f"//MC values for state: {[str(f) for f in s.feature_model.get_features()]} -> {self.Q[s]}/{self.N[s]} = {self.score(s)}")

    def __str__(self) -> str:
        return f"MonteCarlo basic (sc:{str(self.stopping_condition)})"
