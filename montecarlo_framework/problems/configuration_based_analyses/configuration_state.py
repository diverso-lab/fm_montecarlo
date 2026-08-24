import random 
from abc import abstractmethod

from flamapy.metamodels.configuration_metamodel.models.configuration import Configuration
from flamapy.metamodels.fm_metamodel.models import Feature
from flamapy.metamodels.bdd_metamodel.operations import random_configuration

from montecarlo_framework.models.problem import State, Action
from montecarlo_framework.models.feature_model import FMConfiguration


class ConfigurationState(State):
    """A state represents a configuration of a feature model."""

    def __init__(self, configuration: FMConfiguration) -> None:
        self.configuration = configuration
        self._hash_value = hash(configuration)
        self._actions = None

    def actions(self) -> list[Action]:
        if self._actions is not None:
            return self._actions

        self._actions = [SelectFeature(feature) for feature in self.configuration.get_configurable_features()]
        return self._actions

    def successors(self, action: Action) -> list[State]:
        new_config = FMConfiguration.from_configuration(self.configuration)
        new_config.add_feature(action.feature)
        return [self.configuration_transition_function(new_config)]

    def nof_successors(self) -> int:
        return len(self.configuration.get_configurable_features())

    def random_successor(self) -> tuple[State, Action]:
        random_feature = random.choice(self.configuration.get_configurable_features())
        new_config = FMConfiguration.from_configuration(self.configuration)
        new_config.add_feature(random_feature)
        action = SelectFeature(random_feature)
        state = self.configuration_transition_function(new_config)
        return (state, action)

    def get_random_terminal_state(self) -> State:
        #return self.get_random_terminal_state_bdd()
        new_config = FMConfiguration.from_configuration(self.configuration)
        state = self.configuration_transition_function(new_config)
        while not state.is_terminal():
            random_feature = random.choice(state.configuration.get_configurable_features())
            state.configuration.add_feature(random_feature)
        return state

    def get_random_terminal_state_bdd(self) -> State:
        """Return a random terminal state from this state using the BDD sampling."""
        assert self.configuration.fm.bdd_model is not None
        elements = {f.name: True for f in self.configuration.get_selected_features()}
        random_config = random_configuration(self.configuration.fm.bdd_model, Configuration(elements))
        selected_features = [] 
        unselected_features = [] 
        selected_variables = [] 
        unselected_variables = []
        for feature_name, selected in random_config.elements.items():
            if selected:
                selected_features.append(self.configuration.fm.get_feature_by_name(feature_name))
                selected_variables.append(self.configuration.fm.sat_model.variables[feature_name])
            else:
                unselected_features.append(self.configuration.fm.get_feature_by_name(feature_name))
                unselected_variables.append(-self.configuration.fm.sat_model.variables[feature_name])
        fm_config = FMConfiguration(self.configuration.fm, selected_features, unselected_features, selected_variables, unselected_variables)
        return self.configuration_transition_function(fm_config)

    def is_terminal(self) -> bool:
        return self.configuration.is_valid_configuration() or not self.configuration.get_configurable_features()

    def is_valid(self) -> bool:
        return self.configuration.is_valid_configuration()

    def __hash__(self) -> int:
        return self._hash_value

    def __eq__(self, other: object) -> bool:
        return isinstance(other, ConfigurationState) and self.configuration == other.configuration

    def __str__(self) -> str:
        return str(self.configuration)

    @abstractmethod
    def configuration_transition_function(self, configuration: FMConfiguration) -> 'ConfigurationState':
        pass


class SelectFeature(Action):
    
    @staticmethod
    def get_name() -> str:
        return 'Select feature'

    def __init__(self, feature: Feature) -> None:
        self.feature = feature

    def cost(self, state1: 'ConfigurationState', state2: 'ConfigurationState') -> float:
        return 1.0

    def is_applicable(self, state: 'ConfigurationState') -> bool:
        if self.feature in state.configuration.get_selected_features():
            return False 
        return state.configuration.is_valid_partial_configuration_with_feature(self.feature)

    def __str__(self) -> str:
        return f"{self.get_name()} '{str(self.feature)}'"

    def execute(self, state: State) -> State:
        pass
