from abc import ABC, abstractmethod
from typing import List, Any


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
    def execute(self, context: Any) -> Any:
        """Return the object resulting of applying this action to the given context."""
        pass

    @abstractmethod
    def executions(self, context: Any) -> List[Any]:
        """Return the list of possible objects resulting of applying this action to the given context."""
        pass

    @abstractmethod
    def is_applicable(self, context: Any) -> bool:
        """Return True if the action is applicable to the given context, False otherwise."""
        pass
