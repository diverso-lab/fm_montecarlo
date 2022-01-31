import functools
import time
import logging
from dataclasses import dataclass, field
from contextlib import ContextDecorator
from typing import Any, Callable, ClassVar, Dict, Optional

from montecarlo_framework.models import Node
from montecarlo_framework.algorithms.montecarlo_algorithm import MonteCarloAlgorithm


class MonteCarloLoggingError(Exception):
    """A custom exception used to report errors in use of MonteCarloLogging class."""


@dataclass
class MonteCarloLogging(ContextDecorator):
    """Custom logging for Monte Carlo methods.
    
    This provides a decorator @MonteCarloLogging() to trace the execution of MonteCarlo algorithms.
    """

    ALGORITHM_STR = 'Algorithm'  # algorithm's name.
    STEP_STR = 'Step'  # algorithm step, in each step a new state is choosen.
    ALTERNATIVES_STR = 'Alternatives'  # nof of alternatives available to choose from.
    DECISIONS_STR = 'Decisions'  # length of the path solution that corresponds with the nof decisions taken.
    SIMULATIONS_STR = 'Simulations'  # nof simulation per step.
    EVALUATIONS_STR = 'Evaluations'  # nof of times a new terminal state is evaluated.
    POSITIVE_EVALUATIONS_STR = 'Positive Evaluations'  # nof of times the evaluation of a terminal states is possitive.
    TREESIZE_STR = "Tree Size"  # size of the MC tree search, only for those algorithm that built a search tree.
    TIME_STR = 'Time (s)'  # elapsed time to take a decision.
    CHOICE_STR = 'Choice'  # decision made.

    HEADER = [ALGORITHM_STR, STEP_STR, ALTERNATIVES_STR, DECISIONS_STR, CHOICE_STR, SIMULATIONS_STR, EVALUATIONS_STR, POSITIVE_EVALUATIONS_STR, TREESIZE_STR, TIME_STR]

    stats: ClassVar[dict[int, dict[str, Any]]] = field(default={}, init=True, repr=False)
    logger: Optional[Callable[[str], None]] = print
    precision_decimal_digits: int = 4
    _step: int = field(default=0, init=False, repr=False)
    _start_time: float = field(default=None, init=False, repr=False)

    def __post_init__(self) -> None:
        """Initialization."""
        if self.logger:
            #logging.basicConfig(filename='montecarlo_stats.log', level=logging.INFO, format='%(message)s')
            header = ', '.join(MonteCarloStats.HEADER)
            self.logger(f'{header}')

    def add_step(self, 
                 step: int, 
                 algorithm_name: str,
                 alternatives: int,
                 decisions: int,
                 choice: str,
                 simulations: int,
                 evaluations: int,
                 positive_evaluations: int,
                 tree_size: int,
                 time: float):
        MonteCarloStats.stats[step] = {}
        MonteCarloStats.stats[step][MonteCarloStats.ALGORITHM_STR] = algorithm_name
        MonteCarloStats.stats[step][MonteCarloStats.STEP_STR] = step
        MonteCarloStats.stats[step][MonteCarloStats.ALTERNATIVES_STR] = alternatives
        MonteCarloStats.stats[step][MonteCarloStats.DECISIONS_STR] = decisions
        MonteCarloStats.stats[step][MonteCarloStats.CHOICE_STR] = choice
        MonteCarloStats.stats[step][MonteCarloStats.SIMULATIONS_STR] = simulations
        MonteCarloStats.stats[step][MonteCarloStats.EVALUATIONS_STR] = evaluations
        MonteCarloStats.stats[step][MonteCarloStats.POSITIVE_EVALUATIONS_STR] = positive_evaluations
        MonteCarloStats.stats[step][MonteCarloStats.TREESIZE_STR] = tree_size
        MonteCarloStats.stats[step][MonteCarloStats.TIME_STR] = time
        
    @staticmethod
    def serialize(filepath: str):
        if not MonteCarloStats.stats:
            raise MonteCarloStatsError(f"No stats have been recorded. Use @MonteCarloStats decorator over a `choose` method.")

        with open(filepath, 'w+', encoding='utf8') as file:
            header = ', '.join(MonteCarloStats.HEADER)
            file.write(f'{header}\n')
            for step in sorted(MonteCarloStats.stats.keys()):
                line = ', '.join(str(MonteCarloStats.stats[step][h]) for h in MonteCarloStats.HEADER)
                file.write(f"{line}\n")

    def __call__(self, func):
        """Support using Timer as a decorator"""
        @functools.wraps(func)
        def wrapper_choose(algorithm, node):
            self._before(algorithm, node)
            new_node = func(algorithm, node)
            self._after(algorithm, node, new_node)
            return new_node
        return wrapper_choose

    def _before(self, algorithm: MonteCarloAlgorithm, node: Node):
        self._step += 1
        self._start_time = time.perf_counter_ns()

    def _after(self, algorithm: MonteCarloAlgorithm, node: Node, new_node: Node):
        elapsed_time = round((time.perf_counter_ns() - self._start_time) * 1e-9, self.precision_decimal_digits)
        try:
            alternatives = len(algorithm.tree[node])  # ToDo: the real number requires to calculated all successors
            decisions = len(algorithm.tree[node])
            tree_size = len(algorithm.tree)
        except:
            alternatives = len(algorithm.Q)  # ToDo: the real number requires to calculated all successors
            decisions = len(algorithm.Q)
            tree_size = 0
        algorithm_name = algorithm.get_name()
        choice = next(iter(set(new_node.state.configuration.get_selected_features()) - set(node.state.configuration.get_selected_features()))).name
        self.add_step(step=self._step, 
                      algorithm_name=algorithm_name, 
                      alternatives=alternatives, 
                      decisions=decisions, 
                      choice=choice, 
                      simulations=algorithm.get_iteration_stopping_condition().get_value(), 
                      evaluations=0, 
                      positive_evaluations=0, 
                      tree_size=tree_size, 
                      time=elapsed_time)

        # Log the info
        if self.logger:
            line = ', '.join(str(MonteCarloStats.stats[self._step][h]) for h in MonteCarloStats.HEADER)
            self.logger(f'{line}')
