import random
from abc import abstractmethod
from montecarlo4fms.models import State


class ConfigurationState(State):

    def __init__(self, configuration: 'FMConfiguration', data: 'ProblemData'):
        self.configuration = configuration
        self.data = data
        self._hash_value = None
        self._successors = []
        self._applicable_actions = []

    def find_successors(self) -> list:
        if not self._successors:
            successors = []
            for a in self.get_actions():
                configurations = a.executions(self.configuration)
                for c in configurations:
                    if self.data.aafms.is_valid_partial_configuration(c):
                        new_state = self.configuration_transition_function(c)
                        successors.append(new_state)
            self._successors = successors
        return self._successors

    def find_random_successor(self) -> 'State':
        lof_actions = self.get_actions()
        random.shuffle(lof_actions)
        for a in lof_actions:
                configurations = a.executions(self.configuration)
                random.shuffle(configurations)
                for c in configurations:
                    if self.data.aafms.is_valid_partial_configuration(c):
                        new_state = self.configuration_transition_function(c)
                        return new_state
        return None

    @abstractmethod
    def configuration_transition_function(self, config: 'FMConfiguration') -> 'State':
        """Return the a new state with the given configuration."""
        pass

    def get_actions(self) -> list:
        if not self._applicable_actions:
            applicable_actions = []
            if not self.configuration.get_selected_elements():
                applicable_actions.extend(self.data.actions.get_actions()[None])

            for feature in self.configuration.get_selected_elements():
                applicable_actions.extend([a for a in self.data.actions.get_actions()[feature]['Mandatory'] if a.is_applicable(self.configuration)])
                applicable_actions.extend([a for a in self.data.actions.get_actions()[feature]['Optional'] if a.is_applicable(self.configuration)])
            self._applicable_actions = applicable_actions
        
            # for feature in self.configuration.get_selected_elements():
            #     applicable_actions.extend([a for a in self.data.actions.get_actions()[feature]['Mandatory'] if a.is_applicable(self.configuration)])
            
            # if not applicable_actions:
            #     for feature in self.configuration.get_selected_elements():
            #         applicable_actions.extend([a for a in self.data.actions.get_actions()[feature]['Optional'] if a.is_applicable(self.configuration)])
            # self._applicable_actions = applicable_actions
        return self._applicable_actions

    def state_transition_function(self, action: 'Action') -> 'State':
        return self.configuration_transition_function(action.execute(self.configuration))

    def __hash__(self) -> int:
        if not self._hash_value:
            self._hash_value = hash(self.configuration)
        return self._hash_value

    def __eq__(self, other: 'State') -> bool:
        return self.configuration == other.configuration

    def __str__(self) -> str:
        return str(self.configuration)
