from abc import ABC, abstractmethod

from montecarlo_framework.models.problem import State, Action


class Node():
    """A node `n` of the search tree.

    It contains four components:
    - state: the state in the state space to which the node corresponds.
    - parent: the node in the search tree that generated this node.
    - action: action that was applied to the parent to generate the node.
    - path_cost: the cost, tradionally denoted by `g(n)`, of the path from the initial state
                 to the node, as indicated by the parent pointers.
    """

    def __init__(self, state: State, parent: 'Node' = None, action: Action = None):
        self.state = state
        self.parent = parent
        self.action = action
        self.path_cost = 0.0 if parent is None else parent.path_cost + action.cost(parent.state, state) 

    def __str__(self) -> str:
        return f'State: {self.state}, Action: {self.action}, Cost: {0.0 if self.action is None else self.action.cost(self.parent, self.state)}, Path cost: {self.path_cost}'

    def __hash__(self) -> int:
        return hash(self.state)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Node) and self.state == other.state


class NodeValue():
    """Node that stores a value (heuristic, cost,...) and provides a partial order."""

    def __init__(self, node: Node, value: float):
        self.node = node 
        self.value = value 

    def __hash__(self) -> int:
        return hash(self.node)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, NodeValue) and self.node == other.node

    # Define for partial ordering
    def __lt__(self, other: object):
        return self.value < other.value
    
    # Define for partial ordering
    def __gt__(self, other: object):
        return self.value > other.value


# class MCNode():
#     """Monte Carlo node."""

#     def __init__(self, node: Node, q_value: float = 0.0, visits: int = 0):
#         self.node = node 
#         self.q_value = q_value 
#         self.visits = visits


class SearchTree():

    def __init__(self):
        self._tree = {}
    
    def add(self, node: Node):
        self._tree[node.state] = node

    def __contains__(self, state: State) -> bool:
        return state in self._tree

    def get_node(self, state: State) -> Node:
        return self._tree[state]

    def is_root(self, state: State) -> bool:
        return state in self._tree and self._tree[state].parent is None

    def path(self, state: State) -> list[Node]:
        path = []
        while not self.is_root(state):
            path.insert(0, self.get_node(state))
            state = self._tree[state].parent.state
        path.insert(0, self.get_node(state))
        return path

    def size(self) -> int:
        return len(self._tree)


class Solution():

    def __init__(self, terminal_node: Node):
        self.terminal_node = terminal_node 
    
    def get_solution_path(self) -> list[tuple[State, Action]]:
        path = []
        node = self.terminal_node 
        while node.parent is not None:
            path.insert(0, (node.state, node.action))
            node = node.parent 
        path.insert(0, (node.state, node.action))
        return path
        

class Problem(ABC):
    """Problem formulation."""

    def __init__(self) -> None:
        self._solutions = []

    @staticmethod
    @abstractmethod
    def get_name() -> str:
        """Name of the problem."""

    @abstractmethod
    def get_initial_state(self) -> State:
        """Return the initial state of the problem."""

    def add_solution(self, sol: Solution) -> None:
        self._solutions.append(sol)

    def get_solutions(self) -> list[Solution]:
        return self._solutions

