from montecarlo_framework.algorithms.stopping_conditions import StoppingCondition


class NoneStoppingCondition(StoppingCondition):

    def get_value(self):
        return False

    def initialize(self):
        pass

    def update(self):
        pass

    def reached(self) -> bool:
        return False

    def __str__(self) -> str:
        return "None"