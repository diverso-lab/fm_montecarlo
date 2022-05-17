import logging
from collections import defaultdict
from abc import abstractmethod

from montecarlo_framework.algorithms import MonteCarloAlgorithm
from montecarlo_framework.algorithms.stopping_conditions import StoppingCondition
from montecarlo_framework.algorithms.selection_criterias import SelectionCriteria
from montecarlo_framework.models import Problem, State, Node, Solution

from montecarlo_framework.utils.heatmap import Heatmap

class MonteCarloTreeSearch(MonteCarloAlgorithm):
    """
    Monte Carlo Tree Search (MCTS) strategy.
    A search tree is built in an incremental and assymetric manner.
    For each iteration of the algorithm, a tree policy is used to find the most urgent node of the current tree.
    It uses uniform random choices as the default policy for simulations.
    """

    def __init__(self, stopping_condition: StoppingCondition, selection_criteria: SelectionCriteria, decision_stopping_condition: StoppingCondition):
        self.stopping_condition = stopping_condition
        self.selection_criteria = selection_criteria
        self.decision_stopping_condition = decision_stopping_condition
        self.initialize()

    def initialize(self) -> None:
        self.Q: dict[Node, float] = defaultdict(int)  # total reward of each state
        self.N: dict[Node, int] = defaultdict(int)  # total visit count of each state
        self.tree: dict[Node, list[Node]] = dict()  # the MC tree as a dict of node -> children
        self.terminal_states_evaluated: dict[Node, float] = dict()  # terminal states -> reward
        self.total_nof_simulations: int = 0
        self.total_nof_positive_evaluations: int = 0

    @staticmethod
    def get_name() -> str:
        return 'Monte Carlo Tree Search'

    def get_stopping_condition(self) -> StoppingCondition:
        return self.stopping_condition
    
    def get_selection_criteria(self) -> SelectionCriteria:
        return self.selection_criteria

    def get_decision_stopping_condition(self) -> StoppingCondition:
        return self.decision_stopping_condition

    def choose(self, node: Node) -> Node:
        self.get_decision_stopping_condition().initialize()
        while not self.get_decision_stopping_condition().reached():
            self.do_rollout(node)
            self.get_decision_stopping_condition().update()
        return self.get_selection_criteria().best_child(node, self.tree[node], self.Q, self.N)

    def run(self, problem: Problem) -> Solution:
        self.initialize()
        node = Node(problem.get_initial_state())
        
        self.get_stopping_condition().initialize()
        while not node.state.is_terminal() and not self.get_stopping_condition().reached():
            node = self.choose(node)
            self.get_stopping_condition().update()
        return Solution(node) if node is not None else None

    def do_rollout(self, node: Node):
        """Make the search tree one layer better (train for one iteration)."""
        path = self.select(node)
        leaf = path[-1]
        self.expand(leaf)
        reward = self.simulate(leaf.state)
        self.backpropagate(path, reward)

    def select(self, node: Node) -> list[Node]:
        """
        Step 1: Selection.
        Find an expandable/unexplored child node of `state`.
        A node is expandable if it represents a nonterminal state and has unvisited.
        The tree policy is applied recursively until a leaf node is reached.
        Return the list of nodes visited.
        """
        path = [node]
        while node in self.tree and self.tree[node]:  # while state is neither explored nor terminal (if the node has children in the tree means that is not terminal)
            unexplored = self.tree[node] - self.tree.keys()
            if unexplored:  # the node is not fully expanded
                n = unexplored.pop()
                path.append(n)
                return path
            node = self.best_child(node)
            path.append(node)
        return path

    @abstractmethod
    def best_child(self, state: State) -> State:
        """Select the best child of state in the search tree according to a policy tree."""
        pass

    def expand(self, node: Node):
        """
        Step 2: Expansion.
        Update the tree with the children of 'state'.
        """
        if not node in self.tree:
            successors = node.state.all_successors()
            self.tree[node] = [Node(s, node, a) for s, a in successors]

    def simulate(self, state: State) -> float:
        """
        Step 3. Simulation.
        A simulation is rolled out using the default policy (uniform random choices).
        Return the simulation's reward (i.e., reward of the terminal state).
        """
        # while not state.is_terminal():
        #     state, _ = state.random_successor()
        # z = state.reward()
        # return z
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

    def backpropagate(self, path: list[Node], reward: float):
        """
        Step 4. Backpropagation.
        Send the reward back up to the visited nodes in the tree.
        """
        for node in reversed(path):
            self.N[node] += 1
            self.Q[node] += reward

    def get_nof_terminal_states_evaluated(self) -> int:
        return len(self.terminal_states_evaluated)

    def get_total_nof_simulations(self) -> int:
        return self.total_nof_simulations

    def get_total_nof_positive_evaluations(self) -> int:
        return self.total_nof_positive_evaluations