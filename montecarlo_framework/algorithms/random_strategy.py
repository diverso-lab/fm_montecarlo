from montecarlo_framework.models import Problem, Solution, Node
from montecarlo_framework.algorithms import Algorithm
from montecarlo_framework.algorithms.stopping_conditions import StoppingCondition
from montecarlo_framework.utils import AlgorithmStats, get_logger


class RandomStrategy(Algorithm):
    """Random strategy that selects a random successors from the given node."""

    @staticmethod
    def get_name() -> str:
        return 'Random strategy'

    def __init__(self, stopping_condition: StoppingCondition):
        self.stopping_condition = stopping_condition

    def initialize(self) -> None:
        pass 
    
    def get_stopping_condition(self) -> StoppingCondition:
        return self.stopping_condition
        
    @AlgorithmStats('RandomStrategy', logger=None)
    def run(self, problem: Problem) -> Solution:
        node = Node(problem.get_initial_state())
        
        self.get_stopping_condition().initialize()
        while not node.state.is_terminal() and not self.get_stopping_condition().reached():
            node = self.choose(node)
            self.get_stopping_condition().update()
        return Solution(node) if node is not None else None
    
    def choose(self, node: Node) -> Node:
        state, action = node.state.random_successor()
        return Node(state, node, action)
