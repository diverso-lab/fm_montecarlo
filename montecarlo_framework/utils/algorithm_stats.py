import csv
import functools
import time
import tracemalloc
from dataclasses import dataclass, field
from contextlib import ContextDecorator
from typing import Any, Callable, ClassVar, Dict, Optional

from montecarlo_framework.models import State, Problem, Solution
from montecarlo_framework.algorithms.montecarlo_algorithm import MonteCarloAlgorithm
from montecarlo_framework.algorithms.montecarlo_tree_search import MonteCarloTreeSearch
from montecarlo_framework.algorithms import Algorithm
from montecarlo_framework.utils import utils


class AlgorithmStatsError(Exception):
    """A custom exception used to report errors in use of AlgorithmStats class."""


@dataclass
class AlgorithmStats(ContextDecorator):
    """Stats for algorithms.
    
    This provides a decorator @AlgorithmStats(stats_name, logger, precision_decimal_digits)
    to capture statistics of the `run` method in algorithms to find a solution.

    Args:
     - stats_name (str): identifier, name to group and later retrieve the statistics of an algorithm.
     - logger (callable): optional logging function (default log to <<algorithm_name.csv>> file).
                          Example: use `print` to log to console.
     - precision_decimal_digits: number of decimal digits in values for execution times (default 4).
    """

    ALGORITHM_STR = 'Algorithm'  # algorithm's name.
    RUN_STR = 'Run'  # execution number.
    STEPS_STR = 'Steps'  # number of steps perform by the algorithm.
    ITERATIONS_STR = 'Iterations'  # nof of iterations performed by the algorithm to find a solution.
    SIMULATIONS_STR = 'Simulations'  # nof of simulations per decision (the stopping condition value).
    TOTAL_SIMULATIONS_STR = 'Total simulations'  # total nof simulation.
    EVALUATIONS_STR = 'Evaluations'  # nof of times a new terminal state is evaluated.
    POSITIVE_EVALUATIONS_STR = 'Positive Evaluations'  # nof of times the evaluation of a terminal states is possitive.
    TREESIZE_STR = "Tree Size"  # size of the MC tree search, only for those algorithm that built a search tree.
    TIME_STR = 'Time (s)'  # total elapsed time to find a solution.
    MEMORY_STR = 'Memory (MB)'  # peak size of all traced memory blocks used to find a solution.
    SOLUTION_STR = 'Solution'  # the solution

    HEADER = [ALGORITHM_STR, RUN_STR, STEPS_STR, ITERATIONS_STR, SIMULATIONS_STR, TOTAL_SIMULATIONS_STR, EVALUATIONS_STR, POSITIVE_EVALUATIONS_STR, TREESIZE_STR, TIME_STR, MEMORY_STR, SOLUTION_STR]

    stats_name: str
    logger: Optional[Callable[[str], None]] = print  # by default this is replaced in the post_init
    precision_decimal_digits: int = 4
    stats: ClassVar[dict[int, dict[str, Any]]] = {}
    _run: int = field(default=0, init=False, repr=False)
    _start_time: float = field(default=None, init=False, repr=False)
    _memory_peak_usage: int = field(default=None, init=False, repr=False)

    def __post_init__(self) -> None:
        """Initialization."""
        self.stats_name = self.stats_name.lower()
        AlgorithmStats.stats.setdefault(self.stats_name, {})
        if self.logger:
            header = ', '.join(AlgorithmStats.HEADER)
            self.logger(f'{header}')

    def add_step(self, 
                 run: int, 
                 algorithm_name: str,
                 steps: int,
                 iterations: int,
                 simulations: int,
                 total_simulations: int,
                 evaluations: int,
                 positive_evaluations: int,
                 tree_size: int,
                 time: float,
                 memory: int,
                 solution_state: State):
        AlgorithmStats.stats[self.stats_name][run] = {}
        AlgorithmStats.stats[self.stats_name][run][AlgorithmStats.RUN_STR] = run
        AlgorithmStats.stats[self.stats_name][run][AlgorithmStats.ALGORITHM_STR] = algorithm_name
        AlgorithmStats.stats[self.stats_name][run][AlgorithmStats.STEPS_STR] = steps
        AlgorithmStats.stats[self.stats_name][run][AlgorithmStats.ITERATIONS_STR] = iterations
        AlgorithmStats.stats[self.stats_name][run][AlgorithmStats.SIMULATIONS_STR] = simulations
        AlgorithmStats.stats[self.stats_name][run][AlgorithmStats.TOTAL_SIMULATIONS_STR] = total_simulations
        AlgorithmStats.stats[self.stats_name][run][AlgorithmStats.EVALUATIONS_STR] = evaluations
        AlgorithmStats.stats[self.stats_name][run][AlgorithmStats.POSITIVE_EVALUATIONS_STR] = positive_evaluations
        AlgorithmStats.stats[self.stats_name][run][AlgorithmStats.TREESIZE_STR] = tree_size
        AlgorithmStats.stats[self.stats_name][run][AlgorithmStats.TIME_STR] = time
        AlgorithmStats.stats[self.stats_name][run][AlgorithmStats.MEMORY_STR] = memory
        AlgorithmStats.stats[self.stats_name][run][AlgorithmStats.SOLUTION_STR] = solution_state

    @staticmethod
    def get_stats(stats_name: str) -> list[dict[str, Any]]:
        stats_name = stats_name.lower()
        return [AlgorithmStats.stats[stats_name][run] for run in AlgorithmStats.stats[stats_name]]

    @staticmethod
    def get_best_solutions_stats(best_solution: Solution) -> list[dict[str, Any]]:
        best_stats = []
        for stats in AlgorithmStats.stats.values():
            if stats:
                for run in stats.keys():
                    if stats[run][AlgorithmStats.SOLUTION_STR] == best_solution.terminal_node.state:
                        best_stats.append(stats[run])
        return best_stats

    @staticmethod
    def get_total_execution_time(precision_decimal_digits: int) -> float:
        total = 0.0
        for stats in AlgorithmStats.stats.values():
            if stats:
                total += sum(stats[run][AlgorithmStats.TIME_STR] for run in stats)
        return round(total, precision_decimal_digits)

    @staticmethod
    def serialize(stats_name: str, filepath: str):
        stats_name = stats_name.lower()
        if not AlgorithmStats.stats or stats_name not in AlgorithmStats.stats:
            raise AlgorithmStats(f"No stats have been recorded. Use @AlgorithmStats(stats_name) decorator over a `choose` method.")

        with open(filepath, 'w', encoding='utf8', newline='') as file:
            writer = csv.writer(file, delimiter=',')
            writer.writerow(AlgorithmStats.HEADER)
            for step in sorted(AlgorithmStats.stats[stats_name].keys()):
                line = [str(AlgorithmStats.stats[stats_name][step][h]) for h in AlgorithmStats.HEADER]
                writer.writerow(line)

    def __call__(self, func):
        """Support using Timer as a decorator"""
        @functools.wraps(func)
        def wrapper_run(algorithm, problem):
            self._before(algorithm, problem)
            solution = func(algorithm, problem)
            self._after(algorithm, problem, solution)
            return solution
        return wrapper_run

    def _before(self, algorithm: Algorithm, problem: Problem):
        self._run += 1
        tracemalloc.start()
        self._start_time = time.perf_counter_ns()

    def _after(self, algorithm: Algorithm, problem: Problem, solution: Solution):
        elapsed_time = round((time.perf_counter_ns() - self._start_time) * 1e-9, self.precision_decimal_digits)
        _, self._memory_peak_usage = tracemalloc.get_traced_memory()
        self._memory_peak_usage = round(self._memory_peak_usage * 1e-6, self.precision_decimal_digits)
        tracemalloc.reset_peak()

        steps = len(solution.get_solution_path()) - 1
        algorithm_name = algorithm.get_name()
        sc = algorithm.get_stopping_condition().get_value()
        iterations = sc if sc else None

        if isinstance(algorithm, MonteCarloAlgorithm):
            simulations = algorithm.get_decision_stopping_condition().get_value()
            total_simulations = algorithm.get_total_nof_simulations()
            tree_size = len(algorithm.tree) if isinstance(algorithm, MonteCarloTreeSearch) else 0
            evaluations = algorithm.get_nof_terminal_states_evaluated()
            positive_evaluations = algorithm.get_total_nof_positive_evaluations()
        else:
            simulations = 0
            total_simulations = 0
            tree_size = 0
            evaluations = 0
            positive_evaluations = 0
        
        self.add_step(run=self._run,
                      algorithm_name=algorithm_name, 
                      steps=steps, 
                      iterations=iterations, 
                      simulations=simulations,
                      total_simulations=total_simulations,
                      evaluations=evaluations, 
                      positive_evaluations=positive_evaluations, 
                      tree_size=tree_size, 
                      time=elapsed_time,
                      memory=self._memory_peak_usage,
                      solution_state=solution.terminal_node.state)

        # Log the info
        if self.logger:
            line = ', '.join('"' + str(AlgorithmStats.stats[self.stats_name][self._run][h]) + '"'
                             if "'" in str(AlgorithmStats.stats[self.stats_name][self._run][h]) or ',' in str(AlgorithmStats.stats[self.stats_name][self._run][h]) 
                             else str(AlgorithmStats.stats[self.stats_name][self._run][h])
                             for h in AlgorithmStats.HEADER)
            self.logger(f'{line}')
