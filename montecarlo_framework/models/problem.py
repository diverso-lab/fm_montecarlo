from abc import ABC, abstractmethod


class State(ABC):
    """
    Representation of problems for searching strategies.
    
    A representation of a state space must include the representation of the states themselves, 
    as well as the transitions (actions) or set of states directly accessible 
    from a give state (i.e., the successors).
    
    Each kind of problem must extend this class to represent its states.
    """   

    @abstractmethod
    def actions(self) -> list['Action']:
        """All applicable actions in this state."""

    @abstractmethod
    def successors(self, action: 'Action') -> list['State']:
        """The transition model. Return the successors of this state when appling the given action."""

    @abstractmethod
    def random_successor(self) -> tuple['State', 'Action']:
        """Random successor of this state (redefine it for efficiency)."""

    @abstractmethod
    def nof_successors(self) -> int:
        """Number of successors of this state (redefine it for efficiency)."""

    def all_successors(self) -> list[tuple['State', 'Action']]:
        """Return all successors of this state when applying every possible action."""
        successors = []
        for action in self.actions():
            successors.extend([(s, action) for s in self.successors(action)])
        return successors

    def get_random_terminal_state(self) -> 'State':
        """Return a random terminal state from this state (redefine it for efficiency during simulations)."""

    @abstractmethod
    def is_terminal(self) -> bool:
        """The goal test. Determine whether a given state is a goal (terminal) state."""

    @abstractmethod
    def is_valid(self) -> bool:
        """Determines if this state is valid.
        
        Normally, all actions should lead to valid states, 
        so this method can be used for consistency, checking, or statistic purposes.
        """

    @abstractmethod
    def __hash__(self) -> int:
        """States must be hashable."""

    @abstractmethod
    def __eq__(self, other: object) -> bool:
        """States must be comparable."""

    @abstractmethod
    def heuristic(self) -> float:
        """Heuristic estimation of the cost from `self` to the goal."""

    @abstractmethod
    def reward(self) -> float:
        """Assumes `self` is terminal node. Examples of reward: 1=win, 0=loss, 0.5=tie, etc."""


class Action(ABC):
    """Valid actions for the problem."""

    @staticmethod
    @abstractmethod
    def get_name() -> str:
        """Name of the action."""

    @abstractmethod
    def cost(self, source: 'State', target: 'State') -> float:
        """Step cost. Cost of the transition `state1` -> `state2`."""

    @abstractmethod
    def is_applicable(self, state: 'State') -> bool:
        """True if the action is applicable for the given state, False in othercase."""

    @abstractmethod
    def execute(self, state: 'State') -> 'State':
        """Execute the actions."""
