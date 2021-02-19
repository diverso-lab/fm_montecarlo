from montecarlo4fms.algorithms import MonteCarloBasic
from montecarlo4fms.models import State

class MCIterations(MonteCarloBasic):

    def __init__(self, iterations: int = 100):
        super().__init__()
        self.iterations = iterations
        self.it = 0

    def run(self, state: State) -> State:
        self._initialize()
        self.it = 0
        while not self.stopping_condition():
            self.do_rollout(state)
            self.it += 1
        return self.choose(state)

    def stopping_condition(self) -> bool:
        """Return True if the number of iterations is reached."""
        return self.it >= self.iterations
