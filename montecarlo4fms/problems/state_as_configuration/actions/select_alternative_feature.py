from typing import List
from montecarlo4fms.problems.state_as_configuration.actions import SelectFeature
from montecarlo4fms.utils.mc_random import MCRandom as random


class SelectAlternativeFeature(SelectFeature):

    def __init__(self, feature: 'Feature'):
        super().__init__(feature)
        self.alternative_relation = next((r for r in self.feature.get_relations() if r.is_alternative()), None)    # We assume a feature can only have a group relation

    @staticmethod
    def get_name() -> str:
        return "Select alternative feature"

    def execute(self, config: 'FMConfiguration') -> 'FMConfiguration':
        feature = random.choice(self.alternative_relation.children)
        new_config = self.get_config_with_feature(config, feature)
        return new_config

    def executions(self, config: 'FMConfiguration') -> List['FMConfiguration']:
        configurations = []
        for feature in self.alternative_relation.children:
            new_config = self.get_config_with_feature(config, feature)
            configurations.append(new_config)
        return configurations

    def is_applicable(self, config: 'FMConfiguration') -> bool:
        return self.alternative_relation and all(not config.contains(f) for f in self.alternative_relation.children)
