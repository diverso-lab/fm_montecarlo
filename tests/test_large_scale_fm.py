import random

from flamapy.metamodels.configuration_metamodel.models.configuration import Configuration
from flamapy.metamodels.fm_metamodel.transformations.featureide_reader import FeatureIDEReader
from flamapy.metamodels.bdd_metamodel.operations import BDDProductDistribution

from montecarlo_framework.models.feature_model import FM, FMConfiguration
from montecarlo_framework.algorithms import FlatMonteCarlo, UCTMCTS, AStarSearch
from montecarlo_framework.algorithms.stopping_conditions import IterationsStoppingCondition, NoneStoppingCondition
from montecarlo_framework.algorithms.selection_criterias import MaxChild
from montecarlo_framework.models.feature_model.fm_configuration import FMConfiguration
from montecarlo_framework.problems.configuration_based_analyses.valid_min_config_state import ValidMinimumConfigurationState, FindAllValidMinimumConfigurationState, ValidMinConfigProblem
from montecarlo_framework.utils.montecarlo_stats import MonteCarloStats

from montecarlo_framework.models.feature_model import fm_utils

INPUT_MODEL = 'input_fms/linux-2.6.33.3.xml'


def main():
    # Load feature model
    fm = FeatureIDEReader(INPUT_MODEL).transform()

    initial_configuration = fm_utils.initialize_configuration_with_core_features(fm)

    print(f'Initial configuration: {[str(f) for f in initial_configuration.elements]}')

    features = fm_utils.get_features_hash_table(fm)

    open_features = fm_utils.get_open_features(initial_configuration)
    print(f'Open features: {[str(f) for f in open_features]}')
    print(f'#Open features: {len(open_features)}')

    config_with_only_root = Configuration({fm.root: True})
    open_features = fm_utils.get_open_features(config_with_only_root)
    print(f'Open features for root: {[str(f) for f in open_features]}')
    print(f'#Open features for root: {len(open_features)}')


if __name__ == '__main__':
    main()