import csv
from collections import defaultdict

from famapy.metamodels.fm_metamodel.models import FeatureModel, Feature


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

    def __init__(self, feature_model: FeatureModel, mcts_tree_search: dict, mcts_q_values: dict, mcts_visits_count: dict):
        self.feature_model = feature_model 
        self.mcts_tree_search = mcts_tree_search
        self.mcts_q_values = mcts_q_values
        self.mcts_visits_count = mcts_visits_count
        self.knowledge = {}

    def extract_feature_knowledge(self) -> dict[Feature, dict]:
        """Extract the statistics for each feature."""
        feature_rewards = defaultdict(int)
        feature_visits = defaultdict(int)
        for state in self.mcts_tree_search:
            for child in self.mcts_tree_search[state]:
                feature_set = list(child.configuration.get_selected_elements() - state.configuration.get_selected_elements())
                if len(feature_set) == 1:
                    feature = feature_set[0]
                    feature_rewards[feature] += self.mcts_q_values[child]
                    feature_visits[feature] += self.mcts_visits_count[child]
        feature_qvalues = {f: float(feature_rewards[f])/float(feature_visits[f]) if feature_visits[f] > 0 else 0 for f in feature_rewards}

        return self._built_knowledge(feature_rewards, feature_visits, feature_qvalues)
    
    def _built_knowledge(self, feature_rewards: dict[Feature, float], feature_visits: dict[Feature, int], feature_qvalues: dict[Feature, float]) -> dict[Feature, dict]: 
        # To normalize values in range 0..1
        min_value = min(feature_qvalues.values())
        max_value = max(feature_qvalues.values())
        n = max_value - min_value
        # Feature construction knowledge
        for feature in self.feature_model.get_features():
            feature_stats = {}
            if feature in feature_qvalues:
                feature_stats[Heatmap.VISITS_STR] = feature_visits[feature]
                feature_stats[Heatmap.REWARD_STR] = round(feature_rewards[feature], Heatmap.ROUND_DECIMALS)
                feature_stats[Heatmap.QVALUE_STR] = round(feature_qvalues[feature], Heatmap.ROUND_DECIMALS)
                if n > 0:
                    normalized_value = round((feature_qvalues[feature]-min_value) / n, Heatmap.ROUND_DECIMALS)
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

# if __name__ == "__main__":
#     # Read Monte Carlo Q-Values
#     data = read_file("MCTS-heatmap.txt")
    
#     # Normalize values to range 0..1
#     values = list(data.values())
#     min_value = min(values)
#     max_value = max(values)
#     normalized_values = {}
#     heatmap = {}
#     for feature, v in data.items():
#         normalized_values[feature] = (v-min_value)/(max_value-min_value)
#         heatmap[feature] = assign_color(normalized_values[feature])

#     print(normalized_values)
#     print(heatmap)

#     with open("MCTS-heatmap-colors.txt", 'w+') as file:
#         file.write("Feature, Normalized value, Color\n")
#         for f, v, c in zip(heatmap.keys(), normalized_values.values(), heatmap.values()):
#             file.write(f"{f}, {v}, {c}\n")
    