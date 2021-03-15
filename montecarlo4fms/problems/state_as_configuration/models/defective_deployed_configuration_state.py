import os
import sys
import subprocess

from montecarlo4fms.problems.state_as_configuration.models import ConfigurationState

CONFIG_FILE = "montecarlo4fms/problems/defective_configurations/input_pip/configs/config.txt"
INFO_FILE = "montecarlo4fms/problems/defective_configurations/input_pip/configs/info.log"
ERRORS_FILE = "montecarlo4fms/problems/defective_configurations/input_pip/configs/errors.log"


class DefectiveDeployedConfigurationState(ConfigurationState):

    def __init__(self, configuration: 'FMConfiguration', data: 'ProblemData'):
        super().__init__(configuration, data)
        self.is_valid_configuration = self.data.aafms.is_valid_configuration(self.configuration)
        self.errors = None

    def configuration_transition_function(self, config: 'FMConfiguration') -> 'State':
        return DefectiveDeployedConfigurationState(config, self.data)

    def is_terminal(self) -> bool:
        return self.is_valid_configuration or not self.get_actions()

    def reward(self) -> float:
        if not self.is_valid_configuration:
            return -1
        if not self.errors:
            self.deploy_configuration()
            self.errors = self.count_errors()
        if self.errors <= 0:
            return -1

        n = len(self.data.fm.get_features()) - len(self.configuration.get_selected_elements())
        return n * self.errors

    def count_errors(self) -> int:
        # Check errors
        n_errors = 0
        with open(ERRORS_FILE, 'r') as errors_file:
            lines = errors_file.readlines()
            n_errors = lines.count("ERROR: ")

        # Come back to the current environment
        #os.system('/bin/bash --rcfile activate_original_env.sh')

        print(f"Errores: {n_errors}")
        return n_errors


    def deploy_configuration(self) -> int:
        #Create environment to deploy the configurations.

        with open("montecarlo4fms/problems/defective_configurations/input_pip/requirements.txt", 'r') as req_file:
            packages = req_file.readlines()

        # Filter packages by current configuration
        packages_config = [p[:p.index('==')] if '==' in p else p[:p.index('\n')] for p in packages]
        # Read packages from 'requirements.txt'

        packages_config = [p for p in packages_config if self.configuration.contains(self.data.fm.get_feature_by_name(p))]

        # print(f"Packages: {packages}")
        # print(f"packages_config: {packages_config}")
        # print(f"configuration: {[str(f) for f in self.configuration.elements if self.configuration.elements[f]]}")
        # #if self.configuration.elements:
        #    raise Exception

        # Write configuration requirementsimport sys
        with open(CONFIG_FILE, 'w+') as config_file:
            for p in packages_config:
                config_file.write(p + '\n')
            #config_file.writelines(packages_config)

        # Deploy configuration requirements
        #open(ERRORS_FILE, 'w').close()
        with open(INFO_FILE, "w+") as info_file:
            with open(ERRORS_FILE, "w+") as error_file:
                for p in packages_config:
                    subprocess.run(["python", "-m", "pip", "install", "-r", CONFIG_FILE], stdout=info_file, stderr=error_file)
                    print(f"Installing package {p}")
                    #subprocess.Popen(["python", "-m", "pip", "install", p], stdout=info_file, stderr=error_file)
                    #os.system('python -m pip install ' + p + ' &> ' + ERRORS_FILE)
                #subprocess.call(["python", "-m", "pip", "install", "-r", "montecarlo4fms/problems/defective_configurations/input_pip/configs/config.txt", "&>", ERRORS_FILE])

                for p in packages_config:
                    try:
                        with open(INFO_FILE, "a+") as info_file:
                            subprocess.Popen(["python", "-m", "pip", "uninstall", p, "-y"], stdout=info_file)
                        #os.system('python -m pip uninstall ' + p)
                        #subprocess.call(["python", "-m", "pip", "uninstall", p])
                    except:
                        print(f"Error removing package: {p}")
