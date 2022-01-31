from montecarlo_framework.algorithms import (
    RandomStrategy,
    AStarSearch, 
    FlatMonteCarlo, 
    ParallelFlatMonteCarlo,
    UCTMCTS,
    GreedyMCTS
)
from montecarlo_framework.algorithms.stopping_conditions import (
    StoppingCondition,
    NoneStoppingCondition, 
    IterationsStoppingCondition, 
    TimeStoppingCondition
)
from montecarlo_framework.algorithms.selection_criterias import MaxChild


class AlgorithmFactory:

    @staticmethod
    def a_star_search(stopping_condition: StoppingCondition) -> AStarSearch:
       return AStarSearch(stopping_condition=stopping_condition)

    @staticmethod
    def random_strategy(stopping_condition: StoppingCondition) -> RandomStrategy:
        return RandomStrategy(stopping_condition=stopping_condition)

    @staticmethod
    def flat_montecarlo_maxchild(stopping_condition: StoppingCondition, mc_stopping_condition: StoppingCondition) -> FlatMonteCarlo:
        select_crit = MaxChild()
        return FlatMonteCarlo(stopping_condition=stopping_condition, 
                              selection_criteria=select_crit, 
                              decision_stopping_condition=mc_stopping_condition)
    
    @staticmethod
    def parallel_flat_montecarlo_maxchild(stopping_condition: StoppingCondition, mc_stopping_condition: StoppingCondition) -> FlatMonteCarlo:
        select_crit = MaxChild()
        return ParallelFlatMonteCarlo(stopping_condition=stopping_condition, 
                              selection_criteria=select_crit, 
                              decision_stopping_condition=mc_stopping_condition)
    
    @staticmethod
    def uct_mcts_maxchild(stopping_condition: StoppingCondition, mc_stopping_condition: StoppingCondition, exploration_weight: float) -> FlatMonteCarlo:
        select_crit = MaxChild()
        return UCTMCTS(stopping_condition=stopping_condition, 
                       selection_criteria=select_crit, 
                       decision_stopping_condition=mc_stopping_condition,
                       exploration_weight=exploration_weight)
 
    @staticmethod
    def greedy_mcts_maxchild(stopping_condition: StoppingCondition, mc_stopping_condition: StoppingCondition) -> FlatMonteCarlo:
        select_crit = MaxChild()
        return GreedyMCTS(stopping_condition=stopping_condition, 
                          selection_criteria=select_crit, 
                          decision_stopping_condition=mc_stopping_condition)
