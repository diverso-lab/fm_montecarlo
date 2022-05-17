from collections import defaultdict
import multiprocessing

from montecarlo_framework.algorithms import MonteCarloAlgorithm
from montecarlo_framework.algorithms.stopping_conditions import StoppingCondition
from montecarlo_framework.algorithms.selection_criterias import SelectionCriteria
from montecarlo_framework.models import Problem, State, Node, Solution

from montecarlo_framework.utils.montecarlo_stats import MonteCarloStats
from montecarlo_framework.utils.algorithm_stats import AlgorithmStats
from montecarlo_framework.utils.algorithm_logger import get_logger


class FlatMonteCarlo(MonteCarloAlgorithm):
    """
    Basic implementation of the Monte Carlo strategy.
    It performs a default policiy for simulations, where uniform random selection are made.
    The chooses the best state according to a criteria.
    """

    def __init__(self, 
                 stopping_condition: StoppingCondition, 
                 selection_criteria: SelectionCriteria, 
                 decision_stopping_condition: StoppingCondition):
        self.stopping_condition = stopping_condition
        self.selection_criteria = selection_criteria
        self.decision_stopping_condition = decision_stopping_condition
        self.initialize()

    def initialize(self) -> None:
        self.terminal_states_evaluated: dict[State, float] = dict()  # terminal states -> reward
        self.total_nof_simulations: int = 0
        self.total_nof_positive_evaluations: int = 0

    @staticmethod
    def get_name() -> str:
        return 'Flat Monte Carlo'

    def get_stopping_condition(self) -> StoppingCondition:
        return self.stopping_condition
    
    def get_selection_criteria(self) -> SelectionCriteria:
        return self.selection_criteria

    def get_decision_stopping_condition(self) -> StoppingCondition:
        return self.decision_stopping_condition

    @MonteCarloStats('flat_montecarlo_steps', logger=get_logger('flat_montecarlo_steps'))
    #@MonteCarloStats('flat_montecarlo_steps', logger=print)
    def choose(self, node: Node) -> Node:
        self.Q = defaultdict(int)   # total reward of each state
        self.N = defaultdict(int)   # total visit count of each state

        if node.state.nof_successors() == 0:
            return None 
        elif node.state.nof_successors() == 1:
            state, action = node.state.random_successor()
            return Node(state, node, action)

        self.get_decision_stopping_condition().initialize()
        while not self.get_decision_stopping_condition().reached():
            self.do_rollout(node)
            self.get_decision_stopping_condition().update()
        return self.get_selection_criteria().best_child(node, self.Q.keys(), self.Q, self.N)

    @AlgorithmStats('FlatMonteCarlo', logger=None)
    def run(self, problem: Problem) -> Solution:
        self.initialize()
        node = Node(problem.get_initial_state())
        
        self.get_stopping_condition().initialize()
        while not node.state.is_terminal() and not self.get_stopping_condition().reached():
            node = self.choose(node)
            self.get_stopping_condition().update()
        return Solution(node) if node is not None else None

    def do_rollout(self, node: Node):
        """Perform a simulation and store the statistics."""
        child, action = node.state.random_successor()
        child_node = Node(child, node, action)
        reward = self.simulate(child)
        self.Q[child_node] += reward
        self.N[child_node] += 1

    def simulate(self, state: State) -> float:
        """A simulation is rolled out using uniform random choices.

        Return the simulation's reward (i.e., reward of the terminal state).
        """
        self.total_nof_simulations += 1
        terminal_state = state.get_random_terminal_state()
        if terminal_state in self.terminal_states_evaluated:
            reward = self.terminal_states_evaluated[terminal_state]
        else:
            reward = terminal_state.reward()
            self.terminal_states_evaluated[terminal_state] = reward
            if reward > 0:
                self.total_nof_positive_evaluations += 1
        return reward

    def get_nof_terminal_states_evaluated(self) -> int:
        return len(self.terminal_states_evaluated)

    def get_total_nof_simulations(self) -> int:
        return self.total_nof_simulations

    def get_total_nof_positive_evaluations(self) -> int:
        return self.total_nof_positive_evaluations