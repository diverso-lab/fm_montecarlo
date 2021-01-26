from configuration_state import ConfigurationState
from core.fm_godelization import FMGodelization

class ConfigurationsSample():
    """
    Represent a set of configurations.
    Configurations are stored and managed by their identifiers for efficiency.
    Use of a godelization function to assign a unique identifier number to each configuration.
    """

    def __init__(self, feature_model: 'FeatureModel'):
        self._feature_model = feature_model
        self._fm_godelization = FMGodelization(feature_model)
        self._configurations = set() # Set of identifiers.

    def add_configuration(self, config: 'Configuration'):
        """Add the given configuration to the sample."""
        config_number = self._fm_godelization.godelization(config)
        self._configurations.add(config_number)

    def contains(self, config: 'Configuration') -> bool:
        """Returns True if the sample has the given configuration."""
        config_number = self._fm_godelization.godelization(config)
        return config_number in self._configurations

    def remove(self, config: 'Configuration'):
        """Remove a configuration from the sample."""
        config_number = self._fm_godelization.godelization(config)
        self._configurations.remove(config_number)

    def get_configurations(self) -> list['ConfigurationState']:
        """Returns the list of configurations in the sample."""
        return [ConfigurationState(self._feature_model, self._fm_godelization.degodelization(c)) for c in self._configurations]

    def size(self) -> int:
        return len(self._configurations)
