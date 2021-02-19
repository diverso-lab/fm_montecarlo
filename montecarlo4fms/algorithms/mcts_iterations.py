from montecarlo4fms.algorithms import MonteCarloTreeSearch
from montecarlo4fms.models import State

class MCTSIterations(MonteCarloTreeSearch):

    def __init__(self, exploration_weight: float = 0.5, iterations: int = 100):
        super().__init__(exploration_weight)
        self.iterations = iterations
        self.it = 0

    def run(self, state: State) -> State:
        self.it = 0
        while not self.stopping_condition():
            self.do_rollout(state)
            self.it += 1
        return self.choose(state)

    def stopping_condition(self) -> bool:
        """Return True if the number of iterations is reached."""
        return self.it >= self.iterations
