import csv
from collections import defaultdict

from flamapy.metamodels.fm_metamodel.models import FeatureModel, Feature
from montecarlo_framework.models import State


class Heatmap():
    ROUND_DECIMALS = 2

    COLORS = {0.0: 'BLUE',      # We use also 'WHITE' for unexplored features.
              0.2: 'GREEN',
              0.4: 'YELLOW',
              0.6: 'ORANGE',
              0.8: 'RED'}

    FEATURE_STR = 'Feature'
    VISITS_STR = 'Visits'
    REWARD_STR = 'Acc. Reward'
    QVALUE_STR = 'Q-value'
    NORMALIZED_STR = 'Normalized value'
    COLOR_STR = 'Color'

    HEADER = [FEATURE_STR, VISITS_STR, REWARD_STR, QVALUE_STR, NORMALIZED_STR, COLOR_STR]

    def __init__(self, feature_model: FeatureModel, mcts_tree_search: dict, mcts_q_values: dict, mcts_visits_count: dict, state: State):
        self.feature_model = feature_model 
        self.mcts_tree_search = mcts_tree_search
        self.mcts_q_values = mcts_q_values
        self.mcts_visits_count = mcts_visits_count
        self.state = state
        self.knowledge = {}

    def extract_feature_knowledge(self) -> dict[Feature, dict]:
        """Extract the statistics for each feature."""
        feature_rewards = defaultdict(int)
        feature_visits = defaultdict(int)
        for state in self.mcts_tree_search[self.state]:
            feature_set = sorted(set(state.configuration.get_selected_elements()) - set(self.state.configuration.get_selected_elements()))
            if len(feature_set) == 1:
                feature = feature_set[0]
                feature_rewards[feature] = self.mcts_q_values[state]
                feature_visits[feature] += self.mcts_visits_count[state]
        feature_qvalues = {f: float(feature_rewards[f])/float(feature_visits[f]) if feature_visits[f] > 0 else 0 for f in feature_rewards}

        return self._built_knowledge(feature_rewards, feature_visits, feature_qvalues)
    
    def _built_knowledge(self, feature_rewards: dict[Feature, float], feature_visits: dict[Feature, int], feature_qvalues: dict[Feature, float]) -> dict[Feature, dict]: 
        # To normalize values in range 0..1
        values = [feature_qvalues[f] for f in feature_qvalues if feature_visits[f] > 0]
        min_value = min(values)
        max_value = max(values)
        n = max_value - min_value
        # Feature construction knowledge
        for feature in feature_qvalues:
            feature_stats = {}
            if feature_visits[feature] > 0:
                feature_stats[Heatmap.VISITS_STR] = feature_visits[feature]
                feature_stats[Heatmap.REWARD_STR] = round(feature_rewards[feature], Heatmap.ROUND_DECIMALS)
                feature_stats[Heatmap.QVALUE_STR] = round(feature_qvalues[feature], Heatmap.ROUND_DECIMALS)
                if n > 0:
                    normalized_value = round((feature_qvalues[feature]-min_value) / n, Heatmap.ROUND_DECIMALS)
                elif feature_qvalues[feature] > 0:
                    normalized_value = feature_qvalues[feature] / feature_qvalues[feature]
                else: 
                    normalized_value = feature_qvalues[feature]
                    
                feature_stats[Heatmap.NORMALIZED_STR] = normalized_value
                feature_stats[Heatmap.COLOR_STR] = self._assign_color(normalized_value)
            else:
                feature_stats[Heatmap.VISITS_STR] = 0
                feature_stats[Heatmap.REWARD_STR] = 0
                feature_stats[Heatmap.QVALUE_STR] = 0
                feature_stats[Heatmap.NORMALIZED_STR] = 0
                feature_stats[Heatmap.COLOR_STR] = 'WHITE'
            self.knowledge[feature] = feature_stats
        return self.knowledge 

    def _assign_color(self, value: float) -> str:
        for v, c in reversed(Heatmap.COLORS.items()):
            if value >= v:
                return c

    def serialize(self, filepath: str): 
        with open(filepath, 'w+') as file:
            header = ", ".join(Heatmap.HEADER)
            file.write(f"{header}\n")
            for feature in sorted(self.knowledge.keys()):
                line_data = [feature.name]
                for field in Heatmap.HEADER[1:]:
                    line_data.append(str(self.knowledge[feature][field]))
                line = ", ".join(line_data)
                file.write(f"{line}\n")