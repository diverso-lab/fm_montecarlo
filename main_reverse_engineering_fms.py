import time
import sys
from functools import reduce

from famapy.metamodels.fm_metamodel.models import FeatureModel, FMConfiguration, Feature
from famapy.metamodels.fm_metamodel.transformations import FeatureIDEParser, UVLWritter
from famapy.metamodels.pysat_metamodel.transformations import CNFReader
from famapy.metamodels.fm_metamodel.utils import AAFMsHelper

from montecarlo4fms.problems.reverse_engineering.models import FMState
from montecarlo4fms.algorithms import MonteCarloAlgorithms
from montecarlo4fms.utils import MCTSStatsRE

INPUT_PATH = "evaluation/aafmsPythonFramework/"
OUTPUT_RESULTS_PATH = "output_results/"
OUTPUT_RESULTS_FILE = OUTPUT_RESULTS_PATH + "results.csv"
OUTPUT_SUMMARY_FILE = OUTPUT_RESULTS_PATH + "summary.csv"
OUTPUT_PATH = OUTPUT_RESULTS_PATH + "reverse_engineering/"
input_fm_name = "model_simple_paper_excerpt"
input_fm_cnf_name = "model_simple_paper_excerpt-cnf"
iterations = 1000
exploration_weight = 0.5
HEATMAP_FILEPATH = "heatmap_reverse_engineering.csv"


def main():
    print("Reverse engineering problem")

    print("Setting up the problem...")

    input_fm = INPUT_PATH + input_fm_name + ".xml"

    print(f"Loading feature model: {input_fm_name} ...")
    fide_parser = FeatureIDEParser(input_fm, no_read_constraints=True)
    fm = fide_parser.transform()
    print(f"Feature model loaded with {len(fm.get_features())} features, {len(fm.get_constraints())} constraints, {len(fm.get_relations())} relations.")

    # Read the feature model as CNF model with complex constraints
    cnf_reader = CNFReader(INPUT_PATH + input_fm_cnf_name + ".txt")
    cnf_model = cnf_reader.transform()
    
    # Get configurations
    aafms_helper = AAFMsHelper(fm, cnf_model)
    configurations = aafms_helper.get_configurations()

    nc = 1
    for c in configurations:
        print(f"config {nc}: {[str(f) for f in c.get_selected_elements()]}")
        nc += 1
    print(f"#Configurations: {len(configurations)}")

    montecarlo = MonteCarloAlgorithms.uct_iterations_maxchild_random_expansion(iterations=iterations, exploration_weight=exploration_weight)
    #montecarlo = MCTSIterationsRandomPolicy(iterations=iterations)
    #montecarlo = MCTSAnytimeRandomPolicy(seconds=1)
    print(f"Running {type(montecarlo).__name__} with {iterations} iterations.")

    initial_state = FMState(FeatureModel(None), configurations)

    n = 0
    state = initial_state
    start = time.time()
    mcts_stats_re = MCTSStatsRE("reverse_engineering_log.txt")
    while not state.is_terminal():
        print(f"{n}, ", end='', flush=True)    
        #print(f"State {n}: {[str(f) for f in state.feature_model.get_features()]} -> {state.reward()}")
        start_time = time.time()
        new_state = montecarlo.run(state)
        end_time = time.time()
        # heat map
        # heatmap = Heatmap(fm, montecarlo.tree, montecarlo.Q, montecarlo.N, state)
        # heatmap.extract_feature_knowledge()
        # heatmap.serialize(HEATMAP_PATH + input_fm_name + "-step" + str(n) + ".csv")
        mcts_stats_re.add_step(n, montecarlo.tree, montecarlo.Q, montecarlo.N, state, new_state, iterations, end_time - start_time)
        montecarlo.print_MC_values(state)
        state = new_state
        n += 1

    execution_time = time.time() - start
    print(f"Final State {n}: {[str(f) for f in state.feature_model.get_features()]} -> {state.reward()}")

    aafms_helper = AAFMsHelper(state.feature_model)
    new_configurations = aafms_helper.get_configurations()

    print(f"#Features: {len(state.feature_model.get_features())} -> {[str(f) for f in state.feature_model.get_features()]}")

    nc = 1
    for c in new_configurations:
        print(f"config {nc}: {[str(f) for f in c.get_selected_elements()]}")
        nc += 1
    print(f"#Configurations: {len(new_configurations)}")

    relaxed_value = reduce(lambda count, c: count + (aafms_helper.is_valid_configuration(c)), configurations, 0)
    deficit_value = reduce(lambda count, c: count + (c not in new_configurations), configurations, 0)
    surplus_value = reduce(lambda count, c: count + (c not in configurations), new_configurations, 0)
    print(f"Final State {n}: {[str(f) for f in state.feature_model.get_features()]} -> {state.reward()}")
    print(f"Relaxed objective function: {relaxed_value}")
    print(f"Mininal difference objective function (deficit_value + surplus_value): {deficit_value} + {surplus_value} = {deficit_value+surplus_value}")

    path = OUTPUT_PATH + state.feature_model.root.name + "." + UVLWritter.get_destination_extension()
    uvl_writter = UVLWritter(path=path, source_model=state.feature_model)
    uvl_model = uvl_writter.transform()

    print(f"UVL model saved in: {path}")
    print(f"Execution time: {execution_time}")
    montecarlo.print_MC_search_tree()


    #
    # while not state.is_terminal():
    #     n += 1
    #     print(f"State {n}: {[str(f) for f in state.feature_model.get_features()]} -> {state.reward()}")
    #     ns = 1
    #     # for s in state.find_successors():
    #     #     print(f"Suc {ns}: {[str(f) for f in s.feature_model.get_features()]} -> {s.reward()}")
    #     #     ns += 1
    #
    #
    #     #aafms_helper = AAFMsHelper(state.feature_model)
    #     #print(aafms_helper.is_valid_configuration(configurations[0]))
    #     state = mcts.run(state)

    #print(f"Final state: {state}")


    # path = "output_fms/" + state.feature_model.root.name + "." + UVLWritter.get_destination_extension()
    # print(path)
    # uvl_writter = UVLWritter(path=path, source_model=state.feature_model)
    # uvl_model = uvl_writter.transform()
    #
    # aafms_helper = AAFMsHelper(state.feature_model)
    # new_configurations = aafms_helper.get_configurations()
    # print(f"Contained all configurations?: {all(c in new_configurations for c in configurations)}")


    #
    #
    # actions = initial_state.get_actions()
    #
    # print([str(a) for a in actions])
    #
    # successors = initial_state.find_successors()
    # print(successors)
    #
    # ss2 = successors[0].find_successors()
    # print(len(ss2))
    #
    # ss3 = ss2[0].find_successors()
    # print(len(ss3))


if __name__ == '__main__':
    #sys.stdout = open("reverse_engineering_results.txt", "w")
    main()
    #sys.stdout.close()
