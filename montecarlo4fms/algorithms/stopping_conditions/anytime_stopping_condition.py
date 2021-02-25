import time

from montecarlo4fms.algorithms.stopping_conditions import StoppingCondition


class AnytimeStoppingCondition(StoppingCondition):

    def __init__(self, time: int):
        self.time = time
        self._start = 0

    def initialize(self):
        """Initialize the value of the iterations."""
        self._start = time.time()

    def update(self):
        """Update the value of the iterations."""
        pass

    def reached(self) -> bool:
        """Return True if the number of iterations is reached."""
        return (time.time() - self._start) >= self.time
