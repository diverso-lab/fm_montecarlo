from famapy.metamodels.pysat_metamodel.transformations import CNFReader
from famapy.metamodels.fm_metamodel.transformations import FeatureIDEParser, UVLWritter
from famapy.metamodels.fm_metamodel.utils import AAFMsHelper
from montecarlo4fms.problems.state_as_configuration.actions import RandomActionsList, TreeActionsList
from montecarlo4fms.algorithms import MonteCarloAlgorithms
from famapy.metamodels.fm_metamodel.models import FMConfiguration
from montecarlo4fms.problems.state_as_configuration.models import ValidMinimumConfigurationState, ValidConfigurationState, FailureConfigurationState
from montecarlo4fms.problems import ProblemData

from evaluation.jhipster import jhipster


def get_minimum_valid_configuration(fm: 'FeatureModel', aafms_helper: 'AAFMsHelper') -> 'FMConfiguration':
    actions = TreeActionsList(fm)

    problem_data = ProblemData(fm, aafms_helper, actions)
    mcts = MonteCarloAlgorithms.uct_iterations_maxchild(iterations=10, exploration_weight=0.5)
    state = ValidMinimumConfigurationState(FMConfiguration(elements={}), data=problem_data)
    while not state.is_terminal():
        state = mcts.run(state)
        mcts.print_MC_values(state)
    print(f"Reward: {state.reward()}")
    return state.configuration

# PARAMS
MCTS_ITERATIONS = 100
MCTS_EXPLORATION_WEIGHT = 0.5

def get_sample_configurations(fm: 'FeatureModel', aafms_helper: 'AAFMsHelper', sample_size: int, mcts_iterations: int, mcts_exploration_weight: float) -> set:
    actions = TreeActionsList(fm)
    problem_data = ProblemData(fm, aafms_helper, actions)

    # Read the jHipster configurations from the .csv file.
    jhipster_configurations = jhipster.read_jHipster_configurations(jhipster.JHIPSTER_CONFIGS_FILE)  
    problem_data.jhipster_configurations = jhipster_configurations
    sample = {}

    print(f"Sample: ", end='', flush=True)    
    for i in range(sample_size):
        print(f"{i}, ", end='', flush=True)    
        problem_data.sample = sample
        state = FailureConfigurationState(FMConfiguration(elements={}), data=problem_data)

        mcts = MonteCarloAlgorithms.uct_iterations_maxchild(iterations=mcts_iterations, exploration_weight=mcts_exploration_weight)
        while not state.is_terminal():
            state = mcts.run(state)
        sample[i] = state

    return sample


def main():
    # Read the feature model without constraints
    fide_parser = FeatureIDEParser(jhipster.FM_FILE, no_read_constraints=True)
    fm = fide_parser.transform()
    print(f"#Feature model loaded. Features: {len(fm.get_features())}, Constraints: {len(fm.get_constraints())}, Relations: {len(fm.get_relations())}")
    
    # Read the feature model as CNF model with complex constraints
    cnf_reader = CNFReader(jhipster.CNF_FILE)
    cnf_model = cnf_reader.transform()
    
    # AAFMs
    aafms_helper = AAFMsHelper(fm, cnf_model)

    # Get sample of configurations
    sample = get_sample_configurations(fm, aafms_helper, 10, 20, 0.5)
    for s in sample:
        config = sample[s].configuration
        print(f"config {s}: {str(config)}, -> Valid?:{aafms_helper.is_valid_configuration(config)}, -> Errors?:{sample[s].reward() == 1}")

    defective_configs = [s.configuration for s in sample.values() if s.reward() == 1]
    print(f"Defective configs / sample size = {len(defective_configs)} / {len(sample)} = {len(defective_configs)/len(sample)} = {len(defective_configs)/len(sample) * 100} %")
    print(f"#Distinct samples: {len(set(sample.values()))}")

    #print(f"#Configurations: {len(configurations)}")
    config_names = ['JHipster', 'Generator', 'Authentication', 'BackEnd', 'Uaa', 'TestingFrameworks', 'Gatling', 'Maven', 'Docker', 'Server', 'MicroserviceApplication', 'Cucumber']
    
    config_features = {fm.get_feature_by_name(f): True for f in config_names}
    config1 = FMConfiguration(elements=config_features)
    #config1 = get_minimum_valid_configuration(fm, aafms_helper)
    #config1 = all_configs[0]
    #print(f"Valid config: {len(config1.get_selected_elements())} : {config1} -> {aafms_helper.is_valid_configuration(config1)}")

    # Read the jHipster configurations from the .csv file.
    jhipster_configurations = jhipster.read_jHipster_configurations(jhipster.JHIPSTER_CONFIGS_FILE)  

    if aafms_helper.is_valid_configuration(config1):
         jhipster_config = jhipster.filter_configuration(config1, jhipster_configurations)
         #print(f"Filtered config: {jhipster_config}")
    #     error = jhipster.contains_failures(jhipster_config)
    #     print(f"Errors?: {error}")
    # else:
    #     print("Configuración no válida!!")

    # errors = 0
    # for c in jhipster_configurations:
    #     if c['Build'] == 'KO' or c['Compile'] == 'KO':
    #         errors += 1
    # print(f"#Errors: {errors}")

    # jconfigs = jhipster.get_jhipster_configurations("HTTPSession", jhipster_configurations)
    # print(f"#Filter HTTPSession: {len(jconfigs)}")

    # jconfigs = jhipster.get_jhipster_configurations("Protractor", jconfigs)
    # print(f"#Filter Protractor: {len(jconfigs)}")

    # with open("filter_config.csv", 'w+') as ff:
    #     ff.write(str(jconfigs))
    
    # jconfigs = jhipster.get_jhipster_configurations("MicroserviceApplication", jconfigs)
    # print(f"#Filter MicroserviceApplication: {len(jconfigs)}")

    # values = set()
    # for c in jconfigs:
    #     values.add(c['applicationType'])
    # print(values)

    # values = set()
    # for c in configurations:
    #     values.add(c['Log.Build'])
    # print(values)

    # for f in configurations[0].keys():
    #     print(f"{f}: {configurations[0].get(f)}")

    # for f in jhipster_configurations[17267].keys():
    #     print(f"{f}: {jhipster_configurations[17267].get(f)}")

    # values = set()
    # for c in jhipster_configurations:
    #     values.add(c['hibernateCache'])
    # print(values)

    


if __name__ == "__main__":
    main()
    