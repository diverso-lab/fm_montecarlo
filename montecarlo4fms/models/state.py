import random
from abc import ABC, abstractmethod


class State(ABC):
    """
    A representation of a single state.
    An state could be for example a feature model configuration or a board game state.
    MonteCarlo techniques rely on these states (e.g., MCTS works by constructing a tree of these states).
    """

    def find_successors(self) -> list:
        """All possible successors of this state."""
        return [self.state_transition_function(a) for a in self.get_actions()]

    def find_random_successor(self) -> 'State':
        """Random successor of this state (redefine it for more efficient simulation)."""
        return random.choice(self.find_successors())

    @abstractmethod
    def state_transition_function(self, action: 'Action') -> 'State':
        """Return the state resulting of applying the given action to the current state."""
        pass

    @abstractmethod
    def get_actions(self) -> list:
        """Valid applicable actions that can be performed from this state."""
        pass

    @abstractmethod
    def is_terminal(self) -> bool:
        """Returns True if the state represents a terminal node (or it has no successors)."""
        pass

    @abstractmethod
    def reward(self) -> float:
        """Assumes `self` is terminal node. Examples of reward: 1=win, 0=loss, .5=tie, etc."""
        pass

    @abstractmethod
    def __hash__(self) -> int:
        """States must be hashable."""
        pass

    @abstractmethod
    def __eq__(self, other: 'State') -> bool:
        """States must be comparable."""
        pass
