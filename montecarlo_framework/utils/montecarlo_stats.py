import functools
import time
import logging
from dataclasses import dataclass, field
from contextlib import ContextDecorator
from typing import Any, Callable, ClassVar, Dict, Optional

from montecarlo_framework.models import Node
from montecarlo_framework.algorithms.montecarlo_algorithm import MonteCarloAlgorithm


class MonteCarloStatsError(Exception):
    """A custom exception used to report errors in use of MonteCarloStats class."""


@dataclass
class MonteCarloStats(ContextDecorator):
    """Step-wise stats for Monte Carlo methods.
    
    This provides a decorator @MonteCarloStats(stats_name, logger, precision_decimal_digits)
    to capture statistics of the `choose` method in MonteCarlo algorithm.

    Args:
     - stats_name (str): identifier, name to group and later retrieve the statistics of an algorithm.
     - logger (callable): optional logging function (default log to <<algorithm_name.csv>> file).
                          Example: use `print` to log to console.
     - precision_decimal_digits: number of decimal digits in values for execution times (default 4).
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

    stats_name: str
    logger: Optional[Callable[[str], None]] = print  # by default this is replaced in the post_init
    precision_decimal_digits: int = 4
    stats: ClassVar[dict[int, dict[str, Any]]] = {} #field(default={}, init=False, repr=False)
    _step: int = field(default=0, init=False, repr=False)
    _start_time: float = field(default=None, init=False, repr=False)

    def __post_init__(self) -> None:
        """Initialization."""
        self.stats_name = self.stats_name.lower()
        MonteCarloStats.stats.setdefault(self.stats_name, {})
        if self.logger:
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
        MonteCarloStats.stats[self.stats_name][step] = {}
        MonteCarloStats.stats[self.stats_name][step][MonteCarloStats.ALGORITHM_STR] = algorithm_name
        MonteCarloStats.stats[self.stats_name][step][MonteCarloStats.STEP_STR] = step
        MonteCarloStats.stats[self.stats_name][step][MonteCarloStats.ALTERNATIVES_STR] = alternatives
        MonteCarloStats.stats[self.stats_name][step][MonteCarloStats.DECISIONS_STR] = decisions
        MonteCarloStats.stats[self.stats_name][step][MonteCarloStats.CHOICE_STR] = choice
        MonteCarloStats.stats[self.stats_name][step][MonteCarloStats.SIMULATIONS_STR] = simulations
        MonteCarloStats.stats[self.stats_name][step][MonteCarloStats.EVALUATIONS_STR] = evaluations
        MonteCarloStats.stats[self.stats_name][step][MonteCarloStats.POSITIVE_EVALUATIONS_STR] = positive_evaluations
        MonteCarloStats.stats[self.stats_name][step][MonteCarloStats.TREESIZE_STR] = tree_size
        MonteCarloStats.stats[self.stats_name][step][MonteCarloStats.TIME_STR] = time
        
    @staticmethod
    def serialize(stats_name: str, filepath: str):
        stats_name = stats_name.lower()
        if not MonteCarloStats.stats or stats_name not in MonteCarloStats.stats:
            raise MonteCarloStatsError(f"No stats have been recorded. Use @MonteCarloStats(stats_name) decorator over a `choose` method.")

        with open(filepath, 'w+', encoding='utf8') as file:
            header = ', '.join(MonteCarloStats.HEADER)
            file.write(f'{header}\n')
            for step in sorted(MonteCarloStats.stats[stats_name].keys()):
                line = ', '.join(str(MonteCarloStats.stats[stats_name][step][h]) for h in MonteCarloStats.HEADER)
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
                      simulations=algorithm.get_decision_stopping_condition().get_value(), 
                      evaluations=0, 
                      positive_evaluations=0, 
                      tree_size=tree_size, 
                      time=elapsed_time)
        # Log the info
        if self.logger:
            line = ', '.join(str(MonteCarloStats.stats[self.stats_name][self._step][h]) for h in MonteCarloStats.HEADER)
            self.logger(f'{line}')
