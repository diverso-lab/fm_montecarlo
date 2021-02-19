import time
from montecarlo4fms.algorithms import MonteCarloTreeSearch
from montecarlo4fms.models import State

class MCTSAnytime(MonteCarloTreeSearch):

    def __init__(self, exploration_weight: float = 0.5, seconds: int = 1):
        super().__init__(exploration_weight)
        self.time = seconds

    def run(self, state: State) -> State:
        self.start = time.time()
        return super().run()

    def stopping_condition(self) -> bool:
        """Return True if the given gime has been spent, False otherwise."""
        return (time.time() - self.start) >= self.time
