import copy
import random
import subprocess
import os
from abc import abstractmethod

from famapy.metamodels.fm_metamodel.models import FMConfiguration, FeatureModel, Feature
from famapy.metamodels.fm_metamodel.utils import AAFMsHelper
from famapy.metamodels.fm_metamodel.utils import fm_utils

from montecarlo4fms.models import State, Action


class ActivateFeature(Action):
    """
    Add a feature to the configuration.
    """

    def __init__(self, feature: Feature):
        self.feature = feature

    @staticmethod
    def get_name() -> str:
        return "Activate feature"

    def __str__(self) -> str:
        return "Act " + str(self.feature)

    def execute(self, state: 'State') -> 'State':
        configuration = copy.deepcopy(state.configuration)
        configuration.elements[self.feature] = True
        return ConfigurationState(configuration, state.feature_model)


class ConfigurationState(State):
    """
    A state is a configuration.
    """

    def __init__(self, configuration: FMConfiguration, feature_model: FeatureModel, aafms_helper: AAFMsHelper = None):
        self.configuration = configuration
        self.feature_model = feature_model
        self.actions = []
        if aafms_helper:
            self.aafms_helper = aafms_helper
        else:
            self.aafms_helper = AAFMsHelper(feature_model)
        self.is_valid_configuration = self.aafms_helper.is_valid_configuration(self.configuration)
        self.errors = None

    def find_random_successor(self) -> 'State':
        activatable_candidate_features = [f for f in self.feature_model.get_features() if f not in self.configuration.elements or not self.configuration.elements[f]]
        feature = random.choice(activatable_candidate_features)
        return ActivateFeature(feature).execute(self)

    def get_actions(self) -> list:
        if self.actions:
            return self.actions

        actions = []
        activatable_candidate_features = [f for f in self.feature_model.get_features() if f not in self.configuration.elements or not self.configuration.elements[f]]
        for feature in activatable_candidate_features:
            actions.append(ActivateFeature(feature))

        self.actions = actions
        return self.actions

    def is_terminal(self) -> bool:
        """A configuration is terminal if it is valid or no more features can be added."""
        return self.is_valid_configuration or not self.get_actions() #len([f for f in self.feature_model.get_features() if f not in self.configuration.elements or not self.configuration.elements[f]]) == 0 #self.get_actions()

    def reward(self) -> float:
        if self.errors:
            return self.errors
        if not self.is_valid_configuration:
            return -1

        # Create environment to deploy the configurations.
#        subprocess.call(["python", "-m", "venv", "config_env"])
        #subprocess.call(["/bin/bash", "--rcfile", "activate_config_env.sh"])
#        os.system('/bin/bash --rcfile activate_config_env.sh')

        # Read packages from 'requirements.txt'
        with open("montecarlo4fms/problems/defective_configurations/input_pip/requirements.txt", 'r') as req_file:
            packages = req_file.readlines()

            # Filter packages by current configuration
            packages_config = [p for p in packages if any(f.name in p for f in self.configuration.elements if self.configuration.elements[f])]

        print(f"Packages: {packages}")
        print(f"packages_config: {packages_config}")
        print(f"configuration: {[str(f) for f in self.configuration.elements if self.configuration.elements[f]]}")
        if self.configuration.elements:
            raise Exception
        # Write configuration requirements
        CONFIG_FILE = "montecarlo4fms/problems/defective_configurations/input_pip/configs/config.txt"
        with open(CONFIG_FILE, 'w+') as config_file:
            config_file.writelines(packages_config)

        # Deploy configuration requirements
        ERRORS_FILE = "montecarlo4fms/problems/defective_configurations/input_pip/configs/errors.log"
        open(ERRORS_FILE, 'w').close()
        os.system('python -m pip install -r ' + CONFIG_FILE + ' &> ' + ERRORS_FILE)
        #subprocess.call(["python", "-m", "pip", "install", "-r", "montecarlo4fms/problems/defective_configurations/input_pip/configs/config.txt", "&>", ERRORS_FILE])

        for p in packages_config:
            try:
                os.system('python -m pip uninstall ' + p)
                #subprocess.call(["python", "-m", "pip", "uninstall", p])
            except:
                print(f"Error removing package: {p}")

        # Check errors
        n_errors = 0
        with open(ERRORS_FILE, 'r') as errors_file:
            lines = errors_file.readlines()
            n_errors = lines.count("ERROR: ")

        # Come back to the current environment
        #os.system('/bin/bash --rcfile activate_original_env.sh')

        print(f"Errores: {n_errors}")
        self.errors = n_errors
        return self.errors

    def __hash__(self) -> int:
        return hash(self.configuration)

    def __eq__(s1: 'State', s2: 'State') -> bool:
        return s1.configuration == s2.configuration

    def __str__(self) -> str:
        return str(self.configuration)
