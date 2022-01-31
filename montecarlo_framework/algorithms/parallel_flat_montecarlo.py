from collections import defaultdict
import multiprocessing

from montecarlo_framework.algorithms import MonteCarloAlgorithm
from montecarlo_framework.algorithms.stopping_conditions import StoppingCondition
from montecarlo_framework.algorithms.selection_criterias import SelectionCriteria
from montecarlo_framework.models import Problem, State, Node, Solution

from montecarlo_framework.utils.montecarlo_stats import MonteCarloStats
from montecarlo_framework.utils.algorithm_stats import AlgorithmStats
from montecarlo_framework.utils import get_logger


class ParallelFlatMonteCarlo(MonteCarloAlgorithm):
    """
    Basic implementation of the Monte Carlo strategy.
    It performs a default policiy for simulations, where uniform random selection are made.
    The chooses the best state according to a criteria.
    """

    def __init__(self, stopping_condition: StoppingCondition, selection_criteria: SelectionCriteria, decision_stopping_condition: StoppingCondition):
        self.stopping_condition = stopping_condition
        self.selection_criteria = selection_criteria
        self.decision_stopping_condition = decision_stopping_condition
        self.initialize()

    @staticmethod
    def get_name() -> str:
        return 'Parallel Flat Monte Carlo'

    def initialize(self) -> None:
        self.nof_terminal_states_evaluated: int = 0
        self.total_nof_simulations: int = 0
        self.total_nof_positive_evaluations: int = 0

    def get_stopping_condition(self) -> StoppingCondition:
        return self.stopping_condition
    
    def get_selection_criteria(self) -> SelectionCriteria:
        return self.selection_criteria

    def get_decision_stopping_condition(self) -> StoppingCondition:
        return self.decision_stopping_condition

    #@MonteCarloStats('flat_montecarlo_steps', logger=get_logger('flat_montecarlo_steps'))
    #@MonteCarloStats('flat_montecarlo_steps', logger=print)
    def choose(self, node: Node) -> Node:
        self.Q = defaultdict(int)   # total reward of each state
        self.N = defaultdict(int)   # total visit count of each state

        if node.state.nof_successors() == 0:
            return None 
        elif node.state.nof_successors() == 1:
            state, action = node.state.random_successor()
            return Node(state, node, action)

        simulations = self.get_decision_stopping_condition().get_value()
        results_queue = multiprocessing.Queue()
        processes = {}

        for _ in range(simulations):
            child, action = node.state.random_successor()
            child_node = Node(child, node, action)
            p = multiprocessing.Process(target=self.simulate, args=(child, results_queue))
            p.start()
            processes[p] = child_node
        
        for process in processes.keys():
            process.join()
    
        for process in processes.keys():
            child_node = processes[process]
            reward = results_queue.get()
            self.Q[child_node] += reward
            self.N[child_node] += 1
            self.nof_terminal_states_evaluated += 1
            if reward > 0:
                self.total_nof_positive_evaluations += 1
      
        self.total_nof_simulations += simulations
        # print('Q-Values')
        # for n in self.Q.keys():
        #     print(f'{n} -> {self.Q[n]} / {self.N[n]} = {self.Q[n] / self.N[n]}')
        # print('--------')
        return self.get_selection_criteria().best_child(node, self.Q.keys(), self.Q, self.N)

    @AlgorithmStats('ParallelFlatMonteCarlo', logger=None)
    def run(self, problem: Problem) -> Solution:
        self.initialize()
        node = Node(problem.get_initial_state())
        
        self.get_stopping_condition().initialize()
        while not node.state.is_terminal() and not self.get_stopping_condition().reached():
            node = self.choose(node)
        return Solution(node) if node is not None else None

    def do_rollout(self, node: Node, results_queue):
        """Perform a simulation and store the statistics."""
        child, action = node.state.random_successor()
        reward = self.simulate(child)
        result = (child, reward)
        results_queue.put(result)

    def simulate(self, state: State, results_queue: multiprocessing.Queue) -> float:
        """A simulation is rolled out using uniform random choices.

        Return the simulation's reward (i.e., reward of the terminal state).
        """
        z = state.get_random_terminal_state().reward()
        results_queue.put(z)
        return z
    
    def get_nof_terminal_states_evaluated(self) -> int:
        return self.nof_terminal_states_evaluated

    def get_total_nof_simulations(self) -> int:
        return self.total_nof_simulations

    def get_total_nof_positive_evaluations(self) -> int:
        return self.total_nof_positive_evaluations
