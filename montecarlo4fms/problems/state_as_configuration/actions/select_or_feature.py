from typing import List
from montecarlo4fms.problems.state_as_configuration.actions import SelectFeature
from montecarlo4fms.utils.mc_random import MCRandom as random


class SelectOrFeature(SelectFeature):

    def __init__(self, feature: 'Feature'):
        super().__init__(feature)
        self.or_relation = next((r for r in self.feature.get_relations() if r.is_or()), None)    # We assume a feature can only have a group relation

    @staticmethod
    def get_name() -> str:
        return "Select or feature"

    def execute(self, config: 'FMConfiguration') -> 'FMConfiguration':
        possible_features = [f for f in self.or_relation.children if not config.contains(f)]
        feature = random.choice(possible_features)
        new_config = self.get_config_with_feature(config, feature)
        return new_config

    def executions(self, config: 'FMConfiguration') -> List['FMConfiguration']:
        configurations = []
        for feature in self.or_relation.children:
            if not config.contains(feature):
                new_config = self.get_config_with_feature(config, feature)
                configurations.append(new_config)
        return configurations

    def is_applicable(self, config: 'FMConfiguration') -> bool:
        return self.or_relation and any(not config.contains(f) for f in self.or_relation.children)
