import time

from montecarlo4fms.algorithms.stopping_conditions import StoppingCondition


class AnytimeStoppingCondition(StoppingCondition):

    def __init__(self, seconds: int):
        self.seconds = seconds
        self._start = 0

    def get_value(self):
        return self.seconds

    def initialize(self):
        """Initialize the value of the iterations."""
        self._start = time.time()

    def update(self):
        """Update the value of the iterations."""
        pass

    def reached(self) -> bool:
        """Return True if the number of iterations is reached."""
        return (time.time() - self._start) >= self.seconds

    def __str__(self) -> str:
        return f"time={self.get_value()}s"
