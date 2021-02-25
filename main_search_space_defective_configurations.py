import cProfile

from famapy.metamodels.fm_metamodel.models import FeatureModel, FMConfiguration
from famapy.metamodels.fm_metamodel.transformations import FeatureIDEParser
from famapy.metamodels.fm_metamodel.utils import AAFMsHelper

from montecarlo4fms.models import SearchSpace
from montecarlo4fms.problems.defective_configurations.models import ConfigurationState


INPUT_PATH = "montecarlo4fms/problems/defective_configurations/input_fms/"
OUTPUT_PATH = "montecarlo4fms/problems/defective_configurations/output_fms/"
FM_NAME = "pizzas"


def main():
    # Read the feature model
    fide_parser = FeatureIDEParser(INPUT_PATH + FM_NAME + ".xml")
    fm = fide_parser.transform()

    print(f"#Features: {len(fm.get_features())} -> {[str(f) for f in fm.get_features()]}")

    # Get configurations
    aafms_helper = AAFMsHelper(fm)
    configurations = aafms_helper.get_configurations()

    nc = 1
    for c in configurations:
        print(f"config {nc}: {[str(f) for f in c]}")
        nc += 1
    print(f"#Configurations: {len(configurations)}")

    initial_state = ConfigurationState(FMConfiguration(), fm)
    ss = SearchSpace(initial_state=initial_state, max_depth=20)

    nof_total_nodes = 0
    for depth in ss.stats['nof_nodes']:
        nof_nodes = ss.stats['nof_nodes'][depth]
        nof_total_nodes += nof_nodes
        print(f"Depth {depth}: {nof_nodes} nodes")
    print(f"Total nodes: {nof_total_nodes}")


    # print(ss.stats)
    # print(ss.stats['nof_nodes'].values)
    # print(f"#Nodes: {sum(ss.stats['nof_nodes'].values)}")

    format = "svg"
    path = OUTPUT_PATH + FM_NAME
    ss.save_graph(path=path, format=format, view=False)

if __name__ == '__main__':
    #cProfile.run("main()")
    main()
