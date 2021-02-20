from abc import ABC, abstractmethod
from typing import List


class Action(ABC):
    """
    A representation of a valid action.
    """

    @abstractmethod
    def get_name(self) -> str:
        """Name of the action."""
        pass

    @abstractmethod
    def execute(self, state: 'State') -> 'State':
        """Return the state resulting of applying this action to the given state."""
        pass

    def __str__(self) -> str:
        return self.get_name()
