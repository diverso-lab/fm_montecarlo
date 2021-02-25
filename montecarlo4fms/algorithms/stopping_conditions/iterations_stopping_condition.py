from montecarlo4fms.algorithms.stopping_conditions import StoppingCondition


class IterationsStoppingCondition(StoppingCondition):

    def __init__(self, iterations: int):
        self.iterations = iterations
        self.initialize()

    def initialize(self):
        """Initialize the value of the iterations."""
        self._it = 0

    def update(self):
        """Update the value of the iterations."""
        self._it += 1

    def reached(self) -> bool:
        """Return True if the number of iterations is reached."""
        return self._it >= self.iterations
