from famapy.metamodels.pysat_metamodel.transformations import CNFReader
from famapy.metamodels.fm_metamodel.transformations import FeatureIDEParser, UVLWritter
from famapy.metamodels.fm_metamodel.utils import AAFMsHelper
from montecarlo4fms.problems.state_as_configuration.actions import RandomActionsList, TreeActionsList
from montecarlo4fms.algorithms import MonteCarloAlgorithms
from famapy.metamodels.fm_metamodel.models import FMConfiguration
from montecarlo4fms.problems.state_as_configuration.models import ValidMinimumConfigurationState, ValidConfigurationState
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

# def find_all_configurations(fm: 'FeatureModel', aafms_helper: 'AAFMsHelper') -> 'FMConfiguration':
#     actions = TreeActionsList(fm)

#     problem_data = ProblemData(fm, aafms_helper, actions)
#     n = 0

#     mcts = MonteCarloAlgorithms.uct_iterations_maxchild(iterations=10, exploration_weight=0.5)
#     state = ValidMinimumConfigurationState(FMConfiguration(elements={}), data=problem_data)
#     while not state.is_terminal():
#         state = mcts.run(state)
#         mcts.print_MC_values(state)
#     print(f"Reward: {state.reward()}")
#     return state.configuration


def main():
    # Read the feature model without constraints
    fide_parser = FeatureIDEParser(jhipster.FM_FILE, no_read_constraints=True)
    fm = fide_parser.transform()
    print(f"#Features: {len(fm.get_features())}, Constraints: {len(fm.get_constraints())}, Relations: {len(fm.get_relations())}")
    #for f in fm.get_features():
    #    print(f"{f.name} -> parent({str(f.parent)})")
    #uvl_writter = UVLWritter("evaluation/jhipster/jhipster.uvl", fm)
    #uvl_writter.transform()

    # Read the feature model as CNF model with complex constraints
    cnf_reader = CNFReader(jhipster.CNF_FILE)
    cnf_model = cnf_reader.transform()
    #print(cnf_model.variables)
    #print(cnf_model.features.items())

    # AAFMs
    aafms_helper = AAFMsHelper(fm, cnf_model)
    #all_configs = aafms_helper.get_configurations()
    #print(f"All Configs: {len(all_configs)}")
    core_features = aafms_helper.get_core_features()

    #print(f"Core Features: {[str(f) for f in core_features]}")

    # Read the jHipster configurations from the .csv
    jhipster_configurations = jhipster.read_jHipster_configurations(jhipster.JHIPSTER_CONFIGS_FILE)

    #print(f"#Configurations: {len(configurations)}")
    config_names = ['JHipster', 'TestingFrameworks', 'Protractor', 'Gatling', 'Generator', 'SpringWebSockets', 'InternationalizationSupport', 'BackEnd', 'Gradle', 'ClusteredSession', 'Authentication', 'Database', 'Application', 'Cucumber', 'Uaa', 'SQL', 'Development', 'MicroserviceGateway', 'H2', 'InMemory', 'Hibernate2ndLvlCache', 'EhCache', 'Production', 'MySQL']
    
    config_features = {fm.get_feature_by_name(f): True for f in config_names}
    config1 = FMConfiguration(elements=config_features)
    config1 = get_minimum_valid_configuration(fm, aafms_helper)
    #config1 = all_configs[0]
    print(f"Valid config: {len(config1.get_selected_elements())} : {config1} -> {aafms_helper.is_valid_configuration(config1)}")

    if aafms_helper.is_valid_configuration(config1):
        jhipster_config = jhipster.filter_configuration(config1, jhipster_configurations)
        print(f"Filtered config: {jhipster_config}")
        error = jhipster.contains_failures(jhipster_config)
        print(f"Errors?: {error}")
    else:
        print("Configuración no válida!!")

    errors = 0
    for c in jhipster_configurations:
        if c['Build'] == 'KO' or c['Compile'] == 'KO':
            errors += 1
    print(f"#Errors: {errors}")

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
    