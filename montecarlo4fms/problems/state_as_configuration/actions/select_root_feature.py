from typing import List
from montecarlo4fms.problems.state_as_configuration.actions import SelectFeature


class SelectRootFeature(SelectFeature):

    def __init__(self, feature: 'Feature'):
        super().__init__(feature)

    @staticmethod
    def get_name() -> str:
        return "Select root feature"

    def execute(self, config: 'FMConfiguration') -> 'FMConfiguration':
        return self.get_config_with_feature(config, self.feature)

    def executions(self, config: 'FMConfiguration') -> List['FMConfiguration']:
        return [self.get_config_with_feature(config, self.feature)]

    def is_applicable(self, config: 'FMConfiguration') -> bool:
        return bool(config.get_selected_elements())
