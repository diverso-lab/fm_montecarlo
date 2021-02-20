import random
from abc import ABC, abstractmethod


class State(ABC):
    """
    A representation of a single state.
    An state could be for example a feature model configuration or a board game state.
    MonteCarlo techniques rely on these states (e.g., MCTS works by constructing a tree of these states).
    """

    def transition_function(self, action: 'Action') -> 'State':
        """The transition function applies an action to the current state and returns the resulting state."""
        return action.execute(self)

    def find_successors(self) -> list:
        """All possible successors of this state."""
        return [self.transition_function(a) for a in self.get_actions()]

    def find_random_successor(self) -> 'State':
        """Random successor of this state (redefine it for more efficient simulation)."""
        return self.transition_function(random.choose(self.get_actions()))

    @abstractmethod
    def get_actions(self) -> list:
        """Valid actions that can be performed from this state."""
        pass

    @abstractmethod
    def is_terminal(self) -> bool:
        """Returns True if the state has no successor."""
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
    def __eq__(s1: 'State', s2: 'State') -> bool:
        """States must be comparable."""
        pass
