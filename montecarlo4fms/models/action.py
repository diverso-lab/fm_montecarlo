from abc import ABC, abstractmethod
from typing import List


class Action(ABC):
    """
    A representation of a valid action.
    """

    @staticmethod
    @abstractmethod
    def get_name() -> str:
        """Name of the action."""
        pass

    @abstractmethod
    def execute(self, state: 'State') -> 'State':
        """Return the state resulting of applying this action to the given state."""
        pass
