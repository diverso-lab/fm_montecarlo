import os
from collections import defaultdict
import functools
from dataclasses import dataclass, field
from contextlib import ContextDecorator
from typing import Any, Callable, ClassVar, Dict, Optional

from famapy.metamodels.fm_metamodel.models import Feature 

from montecarlo_framework.models import Node, State
from montecarlo_framework.algorithms.montecarlo_algorithm import MonteCarloAlgorithm


class MonteCarloHeatmapError(Exception):
    """A custom exception used to report errors in use of MonteCarloHeatmap class."""


@dataclass
class MonteCarloHeatmap(ContextDecorator):
    """Step-wise heatmap for Monte Carlo methods.
    
    This provides a decorator @MonteCarloHeatmap(stats_name, logger, precision_decimal_digits)
    to capture the knowledge of the `choose` method in MonteCarlo algorithm.

    Args:
     - stats_name (str): identifier, name to group and later retrieve the statistics of an algorithm.
     - logger (callable): optional logging function (default log to <<algorithm_name.csv>> file).
                          Example: use `print` to log to console.
     - precision_decimal_digits: number of decimal digits in values for execution times (default 4).
    """

    OUTPUT_RESULTS_PATH = 'results'
    HEATMAP_PATH = os.path.join(OUTPUT_RESULTS_PATH, 'heatmaps')

    ROUND_DECIMALS = 2

    FEATURE_STR = 'Feature'
    VISITS_STR = 'Visits'
    REWARD_STR = 'Acc. Reward'
    QVALUE_STR = 'Q-value'
    NORMALIZED_STR = 'Normalized value'
    COLOR_STR = 'Color'

    COLORS = {0.0: 'BLUE',      # We use also 'WHITE' for unexplored features.
              0.2: 'GREEN',
              0.4: 'YELLOW',
              0.6: 'ORANGE',
              0.8: 'RED'}

    HEADER = [FEATURE_STR, VISITS_STR, REWARD_STR, QVALUE_STR, NORMALIZED_STR, COLOR_STR]

    stats_name: str
    _step: int = field(default=0, init=False, repr=False)

    def __post_init__(self) -> None:
        """Initialization."""
        self.stats_name = self.stats_name.lower()
        if not os.path.exists(MonteCarloHeatmap.HEATMAP_PATH):
            os.makedirs(MonteCarloHeatmap.HEATMAP_PATH)

    def generate_heatmap(self, 
                         step: int, 
                         tree_search: dict,
                         q_values: dict,
                         visits_count: dict,
                         node: Node) -> dict[Feature, dict]:
        """Extract the statistics for each feature."""
        feature_rewards = defaultdict(int)
        feature_visits = defaultdict(int)
        for n in tree_search[node]:
            feature_set = sorted(set(n.state.configuration.get_selected_features()) - set(node.state.configuration.get_selected_features()))
            if len(feature_set) == 1:
                feature = feature_set[0]
                feature_rewards[feature] = q_values[n]
                feature_visits[feature] += visits_count[n]
        feature_qvalues = {f: float(feature_rewards[f])/float(feature_visits[f]) if feature_visits[f] > 0 else 0 for f in feature_rewards}

        knowledge = self._built_knowledge(feature_rewards, feature_visits, feature_qvalues)
        filename = f'{self.stats_name}_step{step}.csv'
        filepath = os.path.join(MonteCarloHeatmap.HEATMAP_PATH, filename)
        self.serialize(filepath, knowledge)
    
    def _built_knowledge(self, feature_rewards: dict[Feature, float], feature_visits: dict[Feature, int], feature_qvalues: dict[Feature, float]) -> dict[Feature, dict]: 
        knowledge = {}
        # To normalize values in range 0..1
        values = [feature_qvalues[f] for f in feature_qvalues if feature_visits[f] > 0]
        min_value = min(values)
        max_value = max(values)
        n = max_value - min_value
        # Feature construction knowledge
        for feature in feature_qvalues:
            feature_stats = {}
            if feature_visits[feature] > 0:
                feature_stats[MonteCarloHeatmap.VISITS_STR] = feature_visits[feature]
                feature_stats[MonteCarloHeatmap.REWARD_STR] = round(feature_rewards[feature], MonteCarloHeatmap.ROUND_DECIMALS)
                feature_stats[MonteCarloHeatmap.QVALUE_STR] = round(feature_qvalues[feature], MonteCarloHeatmap.ROUND_DECIMALS)
                if n > 0:
                    normalized_value = round((feature_qvalues[feature]-min_value) / n, MonteCarloHeatmap.ROUND_DECIMALS)
                elif feature_qvalues[feature] > 0:
                    normalized_value = feature_qvalues[feature] / feature_qvalues[feature]
                else: 
                    normalized_value = feature_qvalues[feature]
                    
                feature_stats[MonteCarloHeatmap.NORMALIZED_STR] = normalized_value
                feature_stats[MonteCarloHeatmap.COLOR_STR] = self._assign_color(normalized_value)
            else:
                feature_stats[MonteCarloHeatmap.VISITS_STR] = 0
                feature_stats[MonteCarloHeatmap.REWARD_STR] = 0
                feature_stats[MonteCarloHeatmap.QVALUE_STR] = 0
                feature_stats[MonteCarloHeatmap.NORMALIZED_STR] = 0
                feature_stats[MonteCarloHeatmap.COLOR_STR] = 'WHITE'
            knowledge[feature] = feature_stats
        return knowledge 

    def _assign_color(self, value: float) -> str:
        for v, c in reversed(MonteCarloHeatmap.COLORS.items()):
            if value >= v:
                return c

    def serialize(self, filepath: str, knowledge: dict): 
        with open(filepath, 'w+') as file:
            header = ", ".join(MonteCarloHeatmap.HEADER)
            file.write(f"{header}\n")
            for feature in sorted(knowledge.keys()):
                line_data = [feature.name]
                for field in MonteCarloHeatmap.HEADER[1:]:
                    line_data.append(str(knowledge[feature][field]))
                line = ", ".join(line_data)
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

    def _after(self, algorithm: MonteCarloAlgorithm, node: Node, new_node: Node):
        self.generate_heatmap(self._step, algorithm.tree, algorithm.Q, algorithm.N, node)

