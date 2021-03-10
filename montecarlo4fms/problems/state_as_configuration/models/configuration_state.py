import random
from abc import abstractmethod
from montecarlo4fms.models import State


class ConfigurationState(State):

    def __init__(self, configuration: 'FMConfiguration', data: 'ProblemData'):
        self.configuration = configuration
        self.data = data
        self.applicable_actions = None
        self.hash_value = None

    def find_successors(self) -> list:
        successors = []
        for a in self.get_actions():
            configurations = a.executions(self.configuration)
            for c in configurations:
                new_state = self.configuration_transition_function(c)
                successors.append(new_state)
        return successors

    def find_random_successor(self) -> 'State':
        action = random.choice(self.get_actions())
        config = action.execute(self.configuration)
        return self.configuration_transition_function(config)

    @abstractmethod
    def configuration_transition_function(self, config: 'FMConfiguration') -> 'State':
        """Return the a new state with the given configuration."""
        pass

    def get_actions(self) -> list:
        if not self.applicable_actions:
            applicable_actions = []
            if not self.configuration.get_selected_elements():
                applicable_actions.extend(self.data.actions.get_actions()[None])

            for feature in self.configuration.get_selected_elements():
                applicable_actions.extend([a for a in self.data.actions.get_actions()[feature] if a.is_applicable(self.configuration)])

            self.applicable_actions = applicable_actions
        return self.applicable_actions

    def state_transition_function(self, action: 'Action') -> 'State':
        return self.configuration_transition_function(action.execute(self.configuration))

    def __hash__(self) -> int:
        if not self.hash_value:
            self.hash_value = hash(tuple(self.configuration.get_selected_elements()))
        return self.hash_value

    def __eq__(s1: 'State', s2: 'State') -> bool:
        return s1.configuration == s2.configuration

    def __str__(self) -> str:
        return str(self.configuration)
