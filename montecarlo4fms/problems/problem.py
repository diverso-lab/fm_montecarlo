from abc import ABC, abstractmethod

class Problem(ABC):

    @abstractmethod
    def get_problem_name(self):
        """Name of the problem."""
        pass

    @abstractmethod
    def get_initial_state(self):
        """The initial state for the problem."""
        pass

    @abstractmethod
    def get_result_state(self):
        """The result state after solving the the problem."""
        pass

    @abstractmethod
    def solve(self):
        """Execute the algorithm to resolve the problem."""
        pass

    @abstractmethod
    def get_montecarlo_algorithm(self):
        """Return the instance of the montercarlo method to use."""
        pass

    @abstractmethod
    def get_state_type(self):
        """Return the type instance for the states."""
        pass

    @abstractmethod
    def get_stats(self):
        """Return stats of the problem (execution times, status, parameters,...)."""
        pass
