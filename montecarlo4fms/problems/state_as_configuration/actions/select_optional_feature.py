from typing import List
from montecarlo4fms.problems.state_as_configuration.actions import SelectFeature
from montecarlo4fms.utils.mc_random import MCRandom as randomdom


class SelectOptionalFeature(SelectFeature):

    def __init__(self, feature: 'Feature'):
        super().__init__(feature)
        self.optional_relations = [r for r in self.feature.get_relations() if r.is_optional()]

    @staticmethod
    def get_name() -> str:
        return "Select optional feature"

    def execute(self, config: 'FMConfiguration') -> 'FMConfiguration':
        relations = [r for r in self.optional_relations if not config.contains(r.children[0])]
        relation = random.choice(relations)
        new_config = self.get_config_with_feature(config, relation.children[0])
        return new_config

    def executions(self, config: 'FMConfiguration') -> List['FMConfiguration']:
        configurations = []
        for relation in self.optional_relations:
            if not config.contains(relation.children[0]):
                new_config = self.get_config_with_feature(config, relation.children[0])
                configurations.append(new_config)
        return configurations

    def is_applicable(self, config: 'FMConfiguration') -> bool:
        return any(not config.contains(r.children[0]) for r in self.optional_relations)
