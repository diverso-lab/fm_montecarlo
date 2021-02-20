from montecarlo4fms.models import SearchSpace
from montecarlo4fms.problems.reverse_engineering.models import FMState
from famapy.metamodels.fm_metamodel.models import FeatureModel, FMConfiguration
from famapy.metamodels.fm_metamodel.transformations import FeatureIDEParser
from famapy.metamodels.fm_metamodel.utils import AAFMsHelper


def main():
    # Read the feature model
    fide_parser = FeatureIDEParser("input_fms/pizzas_simple.xml")
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

    initial_state = FMState(None, configurations)
    ss = SearchSpace(initial_state, max_depth=5)

    format = "pdf"
    path = "output_fms/" + fm.root.name
    ss.save_graph(path, format)

if __name__ == '__main__':
    main()
