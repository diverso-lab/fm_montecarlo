from abc import ABC, abstractmethod


class StoppingCondition(ABC):
    """
    It represents a generic stopping condition providing methods for
    initialize, update, and check if the condition is reached.

    Example of stopping conditions are a time constraint or a number of interations.
    """

    @abstractmethod
    def get_value(self):
        """Return the stopping condition value."""
        pass

    @abstractmethod
    def initialize(self):
        """Initialize the value of the stopping condition."""
        pass

    @abstractmethod
    def update(self):
        """Update the value of the stopping condition."""
        pass

    @abstractmethod
    def reached(self) -> bool:
        """Return True if the stopping condition is reached, False otherwise."""
        pass
