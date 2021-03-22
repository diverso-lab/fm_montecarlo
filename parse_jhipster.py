import csv 

from famapy.metamodels.pysat_metamodel.transformations import CNFReader
from famapy.metamodels.fm_metamodel.transformations import FeatureIDEParser
from famapy.metamodels.fm_metamodel.utils import AAFMsHelper

JHIPSTER_CONFIGS_FILE = "jhipster3.6.1-testresults.csv"
FM_FILE = "input_fms/fm-3.6.1refined.xml"
CNF_FILE = "input_fms/fm-3.6.1refined-cnf.txt"

# Mapping of feature names in the FM to names in the .csv for concrete features.
JHISPTER_ALTERNATIVES = {'Docker': 'docker',                           # optional (TRUE, FALSE)
                          'Monolithic': 'monolith',                     # alternative
                          'MicroserviceGateway': 'gateway',             # alternative
                          'MicroserviceApplication': 'microservice',    # alternative
                          'UaaServer': 'uaa',                           # alternative
                          'HTTPSession': 'session',                     # alternative
                          'OAuth2': 'oauth2',                           # alternative
                          'Uaa': 'uaa',                                 # alternative
                          'JWT': 'jwt',                                 # alternative
                          'HazelCast': 'hazelcast',                     # alternative
                          'EhCache': 'ehcache',                         # alternative
                          'Cassandra': 'cassandra',
                          'MongoDB': 'mongodb',
                          'ClusteredSession': 'hazelcast',              # optional
                          'SpringWebSockets': 'spring-websocket'        # optional
                          }

JHISPTER_BOOLEAN_OPTIONALS = {'Docker': 'docker',                           # optional (TRUE, FALSE)
                          
                          'ClusteredSession': 'hazelcast',              # optional
                          'SpringWebSockets': 'spring-websocket'        # optional
                          }

def contains_errors(configuration: 'FMConfiguration', jhipster_configurations: list) -> bool:
    """
    Filter the jHipster configurations according to the given configuration.
    Return true if the configuration is found and contains errors; False otherwise.
    """
    for feature in configuration.get_selected_features():
        if not feature.is_abstract:
            if feature.name in MAPPING_JHISPTER_NAMES:
                configs = filter(lambda c: MAPPING_JHISPTER_NAMES[feature.name] in c.values(), jhipster_configurations)




def read_jHipster_configs(filepath) -> list:
    configs = []
    with open(filepath) as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
        for row in reader:
            configs.append(row)
    return configs


def main():
    # Read the feature model without constraints
    fide_parser = FeatureIDEParser(FM_FILE, no_read_constraints=True)
    fm = fide_parser.transform()
    print(f"#Features: {len(fm.get_features())}, Constraints: {len(fm.get_constraints())}, Relations: {len(fm.get_relations())}")

    # Read the feature model as CNF model with complex constraints
    cnf_reader = CNFReader(CNF_FILE)
    cnf_model = cnf_reader.transform()

    # AAFMs
    aafms_helper = AAFMsHelper(fm, cnf_model)
    core_features = aafms_helper.get_core_features()
    print(f"Core Features: {[str(f) for f in core_features]}")

    # Read the jHipster configurations from the .csv
    configurations = read_jHipster_configs(JHIPSTER_CONFIGS_FILE)

    
    values = set()
    for c in configurations:
        values.add(c['Log.Build'])
    print(values)

    # for f in configurations[0].keys():
    #     print(f"{f}: {configurations[0].get(f)}")




if __name__ == "__main__":
    main()