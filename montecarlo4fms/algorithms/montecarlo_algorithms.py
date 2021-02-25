from montecarlo4fms.algorithms import MonteCarloBasic, UCTAlgorithm, UCTRandomExpansion
from montecarlo4fms.algorithms.stopping_conditions import IterationsStoppingCondition, AnytimeStoppingCondition
from montecarlo4fms.algorithms.selection_criterias import MaxChild


class MonteCarloAlgorithms:

    @staticmethod
    def montecarlo_iterations_maxchild(iterations: int = 100) -> 'MonteCarloBasic':
        stop_cond = IterationsStoppingCondition(iterations=iterations)
        select_crit = MaxChild()
        return MonteCarloBasic(stopping_condition=stop_cond, selection_criteria=select_crit)

    @staticmethod
    def montecarlo_anytime_maxchild(seconds: int = 1) -> 'MonteCarloBasic':
        stop_cond = AnytimeStoppingCondition(time=seconds)
        select_crit = MaxChild()
        return MonteCarloBasic(stopping_condition=stop_cond, selection_criteria=select_crit)

    @staticmethod
    def uct_iterations_maxchild(iterations: int = 100, exploration_weight: float = 0.5) -> 'MonteCarloTreeSearch':
        stop_cond = IterationsStoppingCondition(iterations=iterations)
        select_crit = MaxChild()
        return UCTAlgorithm(stopping_condition=stop_cond, selection_criteria=select_crit, exploration_weight=exploration_weight)

    @staticmethod
    def uct_anytime_maxchild(seconds: int = 1, exploration_weight: float = 0.5) -> 'MonteCarloTreeSearch':
        stop_cond = AnytimeStoppingCondition(time=seconds)
        select_crit = MaxChild()
        return UCTAlgorithm(stopping_condition=stop_cond, selection_criteria=select_crit, exploration_weight=exploration_weight)

    @staticmethod
    def uct_iterations_maxchild_rnd_expansion(iterations: int = 100, exploration_weight: float = 0.5) -> 'MonteCarloTreeSearch':
        stop_cond = IterationsStoppingCondition(iterations=iterations)
        select_crit = MaxChild()
        return UCTRandomExpansion(stopping_condition=stop_cond, selection_criteria=select_crit, exploration_weight=exploration_weight)

    @staticmethod
    def uct_anytime_maxchild_rnd_expansion(seconds: int = 1, exploration_weight: float = 0.5) -> 'MonteCarloTreeSearch':
        stop_cond = AnytimeStoppingCondition(time=seconds)
        select_crit = MaxChild()
        return UCTRandomExpansion(stopping_condition=stop_cond, selection_criteria=select_crit, exploration_weight=exploration_weight)
