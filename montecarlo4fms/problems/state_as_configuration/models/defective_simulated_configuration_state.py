from montecarlo4fms.problems.state_as_configuration.models import ConfigurationState

PACKAGES_WITH_ERRORS_IN_LINUX = ['pyPicosat', 'ebnf']
PACKAGES_WITH_ERRORS_IN_WIN = ['pylgl', 'satyrn', 'pydebqbf', 'SimpleParser']

class DefectiveSimulatedConfigurationState(ConfigurationState):

    def __init__(self, configuration: 'FMConfiguration', data: 'ProblemData'):
        super().__init__(configuration, data)
        self.is_valid_configuration = self.data.aafms.is_valid_configuration(self.configuration)
        self.errors = None
        self.evaluated = False

    def configuration_transition_function(self, config: 'FMConfiguration') -> 'State':
        return DefectiveSimulatedConfigurationState(config, self.data)

    def is_terminal(self) -> bool:
        return self.is_valid_configuration or not self.get_actions()

    def reward(self) -> float:
        if not self.is_valid_configuration:
            return -1
        if not self.errors:
            self.errors = self.count_errors()
            self.evaluated = True
        if self.errors <= 0:
            return -1

        #n = len(self.data.fm.get_features()) - len(self.configuration.get_selected_elements())
        return self.errors

    def count_errors(self) -> int:
        packages_with_errors = []
        linux_feature = self.data.fm.get_feature_by_name("Linux")
        win_feature = self.data.fm.get_feature_by_name("Win")
        if linux_feature in self.configuration.get_selected_elements():
            packages_with_errors = [f for f in self.configuration.get_selected_elements() if f.name in PACKAGES_WITH_ERRORS_IN_LINUX]
        elif win_feature in self.configuration.get_selected_elements():
            packages_with_errors = [f for f in self.configuration.get_selected_elements() if f.name in PACKAGES_WITH_ERRORS_IN_WIN]
        return len(packages_with_errors)
