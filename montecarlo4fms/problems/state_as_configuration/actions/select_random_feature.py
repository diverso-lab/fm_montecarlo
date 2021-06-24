from abc import abstractmethod
from typing import List
from montecarlo4fms.problems.state_as_configuration.actions import SelectFeature
from montecarlo4fms.utils.mc_random import MCRandom as random


class SelectRandomFeature(SelectFeature):

    def __init__(self, feature_model: 'FeatureModel'):
        self.fm = feature_model

    @staticmethod
    def get_name() -> str:
        return "Select random feature"

    def __str__(self) -> str:
        return self.get_name()

    def execute(self, config: 'FMConfiguration') -> 'FMConfiguration':
        possible_features = [f for f in self.fm.get_features() if f not in config.get_selected_elements()]
        feature = random.choice(possible_features)
        return self.get_config_with_feature(config, feature)

    def executions(self, config: 'FMConfiguration') -> List['FMConfiguration']:
        configs = []
        possible_features = [f for f in self.fm.get_features() if f not in config.get_selected_elements()]
        for feature in possible_features:
            configs.append(self.get_config_with_feature(config, feature))
        return configs

    def is_applicable(self, config: 'FMConfiguration') -> bool:
        return any(f not in config.get_selected_elements() for f in self.fm.get_features())
