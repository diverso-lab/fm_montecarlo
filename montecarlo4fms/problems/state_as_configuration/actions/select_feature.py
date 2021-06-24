from abc import abstractmethod
from typing import List
from montecarlo4fms.models import Action
from functools import total_ordering

@total_ordering
class SelectFeature(Action):

    def __init__(self, feature: 'Feature'):
        self.feature = feature

    @staticmethod
    def get_name() -> str:
        return "Select feature"

    def __str__(self) -> str:
        return self.get_name() + " for " + str(self.feature)

    def __lt__(self, other):
        return str(self) < str(other)
    
    def __eq__(self, other: 'SelectFeature') -> bool:
        return str(self) == str(other)

    def get_config_with_feature(self, config: 'FMConfiguration', feature: 'Feature') -> 'FMConfiguration':
        """Return a new configuration with the given feature added."""
        new_config = config.clone()
        new_config.add_element(feature)
        return new_config

    @abstractmethod
    def execute(self, config: 'FMConfiguration') -> 'FMConfiguration':
        pass

    @abstractmethod
    def executions(self, config: 'FMConfiguration') -> List['FMConfiguration']:
        pass

    @abstractmethod
    def is_applicable(self, config: 'FMConfiguration') -> bool:
        pass
