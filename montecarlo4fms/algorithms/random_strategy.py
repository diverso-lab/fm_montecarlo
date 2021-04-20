from montecarlo4fms.models import State
from montecarlo4fms.algorithms.stopping_conditions import StoppingCondition


class RandomStrategy:

    def __init__(self, stopping_condition: StoppingCondition):
        self.stopping_condition = stopping_condition

    def run(self, state: State) -> State:
        return state.find_random_successor()

    def get_iterations_executed(self) -> int:
        return 0

    def __str__(self) -> str:
        return "Random Strategy"
