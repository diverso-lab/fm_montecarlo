import heapq

from montecarlo_framework.algorithms import Algorithm
from montecarlo_framework.algorithms.stopping_conditions import StoppingCondition, NoneStoppingCondition
from montecarlo_framework.models import Problem, Node, NodeValue, Solution
from montecarlo_framework.utils.algorithm_stats import AlgorithmStats
from montecarlo_framework.utils.algorithm_logger import get_logger


class AStarSearch(Algorithm):
    """Implementation of the A* search algorithm.
    
    A* search is a best-first search algorithm which evaluates nodes by combining g(n), 
    the path cost from the start node to node n, and h(n), the estimated cost (heuristic)
    of the cheapest path from `n` to the goal.

    We use the `satellite` class `NodeValue` to store the f(n) values:
        f(n) = g(n) + h(n) = estimated cost of the cheapest solution through n.

    A* search is both complete and optimal. 
    The algorithm is identical to Uniform-Cost Search except that A* uses g + h instead of g.
    """

    def __init__(self, stopping_condition: StoppingCondition):
        self.stopping_condition = stopping_condition

    @staticmethod
    def get_name() -> str:
        return 'A* search'

    def initialize(self) -> None:
        pass 
    
    def get_stopping_condition(self) -> StoppingCondition:
        return self.stopping_condition

    @AlgorithmStats('AStarSearch', logger=None)
    def run(self, problem: Problem) -> Solution:
        node = Node(problem.get_initial_state())
        frontier = []  # Priority queue (heapq)
        explored = {}

        self.get_stopping_condition().initialize()
        while node is not None and not node.state.is_terminal() and not self.get_stopping_condition().reached():
            for action in node.state.actions():
                children = node.state.successors(action)
                for child in children:
                    child_node = Node(child, node, action)
                    if child not in explored or child_node.path_cost < explored[child].path_cost:
                        child_node_value = NodeValue(child_node, child_node.path_cost + child_node.state.heuristic())
                        if child_node in explored:
                            frontier.remove(child_node_value)
                        heapq.heappush(frontier, child_node_value)
                        explored[child] = child_node
            node = heapq.heappop(frontier).node if frontier else None
            self.get_stopping_condition().update()
        return Solution(node) if node else None
