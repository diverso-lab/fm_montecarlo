from famapy.metamodels.pysat_metamodel.transformations import CNFReader
from famapy.metamodels.fm_metamodel.transformations import FeatureIDEParser
from famapy.metamodels.fm_metamodel.utils import AAFMsHelper

from evaluation.jhipster import jhipster


def main():
    # Read the feature model without constraints
    fide_parser = FeatureIDEParser(jhipster.FM_FILE, no_read_constraints=True)
    fm = fide_parser.transform()
    print(f"#Features: {len(fm.get_features())}, Constraints: {len(fm.get_constraints())}, Relations: {len(fm.get_relations())}")

    # Read the feature model as CNF model with complex constraints
    cnf_reader = CNFReader(jhipster.CNF_FILE)
    cnf_model = cnf_reader.transform()

    # AAFMs
    aafms_helper = AAFMsHelper(fm, cnf_model)
    core_features = aafms_helper.get_core_features()
    print(f"Core Features: {[str(f) for f in core_features]}")

    # Read the jHipster configurations from the .csv
    configurations = jhipster.read_jHipster_configs(jhipster.JHIPSTER_CONFIGS_FILE)

    
    values = set()
    for c in configurations:
        values.add(c['Log.Build'])
    print(values)

    # for f in configurations[0].keys():
    #     print(f"{f}: {configurations[0].get(f)}")




if __name__ == "__main__":
    main()