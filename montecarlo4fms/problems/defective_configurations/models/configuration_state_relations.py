import copy
import random
import os
import subprocess
from abc import abstractmethod
from typing import List

from famapy.metamodels.fm_metamodel.models import FMConfiguration, FeatureModel, Feature
from famapy.metamodels.fm_metamodel.utils import AAFMsHelper
from famapy.metamodels.fm_metamodel.utils import fm_utils

from montecarlo4fms.models import State, Action



class ActivateFeature(Action):
    """
    Activate the feature of a mandatory relation.
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
        return ConfigurationStateRelations(configuration, state.feature_model)


class ConfigurationStateRelations(State):
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
        if not self.configuration.elements:
            return ActivateFeature(self.feature_model.root).execute(self)

        relations = self._get_undecided_mandatory_relations()
        if not relations:
            relations = self._get_undecided_optional_relations()
        random_relation = random.choice(relations)
        features = self._get_undecided_features_for_relation(random_relation)
        random_feature = random.choice(features)
        return ActivateFeature(random_feature).execute(self)

    def get_actions(self) -> list:
        if self.actions:
            return self.actions

        if not self.configuration.elements:
            self.actions = [ActivateFeature(self.feature_model.root)]
            return self.actions

        actions = []
        features_selections = []
        undecided_mandatory_relations = self._get_undecided_mandatory_relations()
        if undecided_mandatory_relations:
            # Esta implementación toma la decisión de cada feature como una única configuración (permite analizar feature a feature)
            # La configuración solo se incrementa de 1 en 1 feature en feature.
            for relation in undecided_mandatory_relations:
                undecided_features = self._get_undecided_features_for_relation(relation)
                actions.extend([ActivateFeature(f) for f in undecided_features])

            # Esta implementación toma todas las decisiones obligatorias en una única configuración
            # for relation in undecided_mandatory_relations:
            #     successors_for_relation = self._get_successors_for_relation(relation)
            #     # Successors of mandatory features needs to be mixed.
            #     if not successors:
            #         successors = successors_for_relation
            #     else:
            #         new_successors = []
            #         for s in successors:
            #             for ns in successors_for_relation:
            #                 new_successors.append(ConfigurationState(self.fm_helper, list(dict.fromkeys(s.elements + ns.elements))))
            #         successors = new_successors

        else: # optionals
            undecided_optional_relations = self._get_undecided_optional_relations()
            for relation in undecided_optional_relations:
                undecided_features = self._get_undecided_features_for_relation(relation)
                actions.extend([ActivateFeature(f) for f in undecided_features])

        self.actions = actions
        return self.actions

    def _get_undecided_features_for_relation(self, relation: 'Relation') -> List['Feature']:
        """List of undecided features of the given relation. That is, features that have not been already selected in the configuration."""
        if not relation.children:
            return []
        elif relation.is_mandatory() or relation.is_optional():
            return relation.children
        elif relation.is_alternative():
            return relation.children
        elif relation.is_or():
            return [child for child in relation.children if child not in self.configuration.elements]
        else: # n..m group cardinality
            return [child for child in relation.children if child not in self.configuration.elements]

    def _get_undecided_mandatory_relations(self) -> List['Relation']:
        """Undecided mandatory relations are those relation that needs to be decided in order to move closer to the next configuration according to the tree hierarchy."""
        res = []
        for feature in self.configuration.elements:
            for r in feature.get_relations():
                if (r.is_mandatory() and r.children[0] not in self.configuration.elements) or (r.is_alternative() and not any(child in self.configuration.elements for child in r.children)) or (r.is_or() and not any(child in self.configuration.elements for child in r.children)):
                    res.append(r)
        return res

    def _get_undecided_optional_relations(self) -> List['Relation']:
        """Undecided optional relations are those relations that may be decided (but not required by the tree hierarchy) in order to move closer to the next configuration."""
        res = []
        for feature in self.configuration.elements:
            for r in feature.get_relations():
                if (r.is_optional() and r.children[0] not in self.configuration.elements) or (r.is_or() and any(child not in self.configuration.elements for child in r.children)):
                    res.append(r)
        return res

    def is_terminal(self) -> bool:
        """A configuration is terminal if it is valid or no more features can be added."""
        return self.is_valid_configuration or not self.get_actions()

    def reward(self) -> float:
        #return 1 if self.is_valid_configuration else -1
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
        #if self.configuration.elements:
        #    raise Exception

        # Write configuration requirements
        CONFIG_FILE = "montecarlo4fms/problems/defective_configurations/input_pip/configs/config.txt"
        with open(CONFIG_FILE, 'w+') as config_file:
            config_file.writelines(packages_config)

        # Deploy configuration requirements
        INFO_FILE = "montecarlo4fms/problems/defective_configurations/input_pip/configs/info.log"
        ERRORS_FILE = "montecarlo4fms/problems/defective_configurations/input_pip/configs/errors.log"
        #open(ERRORS_FILE, 'w').close()
        with open(INFO_FILE, "w+") as info_file:
            with open(ERRORS_FILE, "w+") as error_file:
                subprocess.run(["python", "-m", "pip", "install", "-r", CONFIG_FILE], stdout=info_file, stderr=error_file)
        #os.system('python -m pip install -r ' + CONFIG_FILE + ' &> ' + ERRORS_FILE)
        #subprocess.call(["python", "-m", "pip", "install", "-r", "montecarlo4fms/problems/defective_configurations/input_pip/configs/config.txt", "&>", ERRORS_FILE])

        for p in packages_config:
            try:
                with open(INFO_FILE, "a+") as info_file:
                    subprocess.run(["python", "-m", "pip", "uninstall", p, "-y"], stdout=info_file)
                #os.system('python -m pip uninstall ' + p)
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
