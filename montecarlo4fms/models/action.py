from abc import ABC, abstractmethod
from typing import List
from montecarlo4fms.models import State


class Action(ABC):
    """
    A representation of a valid action.
    """

    @abstractmethod
    def get_name(self) -> str:
        """Name of the action."""
        pass

    @abstractmethod
    def execute(self, state: State) -> List[State]:
        """Return the state(s) resulting of applying the action to the given state."""
        pass

    def __str__(self) -> str:
        return self.get_name()
