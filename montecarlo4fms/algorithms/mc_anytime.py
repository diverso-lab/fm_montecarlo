import time
from montecarlo4fms.algorithms import MonteCarloBasic
from montecarlo4fms.models import State


class MCAnytime(MonteCarloBasic):

    def __init__(self, seconds: int = 1):
        super().__init__()
        self.time = seconds

    def run(self, state: State) -> State:
        self.start = time.time()
        return super().run(state)

    def stopping_condition(self) -> bool:
        """Return True if the given gime has been spent, False otherwise."""
        return (time.time() - self.start) >= self.time
