import csv 
import ast
import random 

from flamapy.metamodels.fm_metamodel.transformations.featureide_reader import FeatureIDEReader

from montecarlo_framework.models.feature_model import FMConfiguration, FM

JHIPSTER_CONFIGS_FILE = "models/jhipster/jhipster3.6.1-testresults.csv"
JHIPSTER_CONFIGS_FAILURES_FILE = "models/jhipster/jhipster3.6.1-configs-failures.csv"
FM_FILE = "models/jHipster.xml"


# Mapping of feature names in the FM to filters to apply to the configurations according the values in the .csv. Feature name in the FM -> (variation point, variant, value_not_selected)
JHIPSTER_FILTERS = {'Docker':                       ('Docker', 'TRUE', 'FALSE'),
                    'MicroserviceApplication':      ('applicationType', 'microservice', '-'),
                    'Monolithic':                   ('applicationType', 'monolith', '-'),
                    'MicroserviceGateway':          ('applicationType', 'gateway', '-'),
                    'UaaServer':                    ('applicationType', 'uaa', '-'),
                    'HTTPSession':                  ('authenticationType', 'session', '-'),
                    'OAuth2':                       ('authenticationType', 'oauth2', '-'),
                    'Uaa':                          ('authenticationType', 'uaa', '-'),
                    'JWT':                          ('authenticationType', 'jwt', '-'),
                    'HazelCast':                    ('hibernateCache', 'hazelcast', 'no'),
                    'EhCache':                      ('hibernateCache', 'ehcache', 'no'),
                    'ClusteredSession':             ('clusteredHttpSession', 'hazelcast', 'no'),
                    'SpringWebSockets':             ('websocket', 'spring-websocket', 'no'),
                    'SQL':                          ('databaseType', 'sql', 'no'),
                    'Cassandra':                    ('databaseType', 'cassandra', 'no'),
                    'MongoDB':                      ('databaseType', 'mongodb', 'no'),
                    'DiskBased':                    ('devDatabaseType', 'DiskBased', '-'),
                    'InMemory':                     ('devDatabaseType', 'InMemory', '-'),
                    'PostgreSQLDev':                ('devDatabaseType', 'postgresql', '-'),
                    'MariaDBDev':                   ('devDatabaseType', 'mariadb', '-'),
                    'MySql':                        ('devDatabaseType', 'mysql', ''),
                    'MySQL':                        ('prodDatabaseType', 'mysql', 'mysql'),
                    'MariaDB':                      ('prodDatabaseType', 'mariadb', '-'),
                    'PostgreSQL':                   ('prodDatabaseType', 'postgresql', '-'),
                    'Gradle':                       ('buildTool', 'gradle', '-'),
                    'Maven':                        ('buildTool', 'maven', '-'),
                    'ElasticSearch':                ('searchEngine', 'elasticsearch', 'no'),
                    'SocialLogin':                  ('enableSocialSignIn', 'TRUE', 'FALSE'),
                    'Libsass':                      ('useSass', 'TRUE', 'FALSE'),
                    'InternationalizationSupport':  ('enableTranslation', 'TRUE', 'FALSE'),
                    'Protractor':                   ('protractor', 'TRUE', 'FALSE'),
                    'Gatling':                      ('gatling', 'TRUE', 'FALSE'),
                    'Cucumber':                     ('cucumber', 'TRUE', 'FALSE')} 


def filter_configuration(configuration: 'FMConfiguration', jhipster_configurations: list) -> dict:
    """Filter the jHipster configurations according to the given configuration and return the dictionary representing the jHipster configuration."""
    configs = list(jhipster_configurations) 
    #print(f"#Total configs: {len(configs)}")        
    
    # Filter the selected features in the given configuration
    selected_feature_names = [f.name for f in configuration.get_selected_features()]
    for feature_name in selected_feature_names:
        if feature_name in JHIPSTER_FILTERS:
            configs = list(filter(lambda c: c[JHIPSTER_FILTERS[feature_name][0]] == JHIPSTER_FILTERS[feature_name][1], configs))
            #print(f"#Filter {feature_name}: {len(configs)}")
    
    optional_features_not_selected = [f_name for f_name in JHIPSTER_FILTERS.keys() if JHIPSTER_FILTERS[f_name][2] != '-' and f_name not in selected_feature_names]
    for feature_name in optional_features_not_selected:
        configs = list(filter(lambda c: c[JHIPSTER_FILTERS[feature_name][0]] == JHIPSTER_FILTERS[feature_name][2] or c[JHIPSTER_FILTERS[feature_name][0]] != JHIPSTER_FILTERS[feature_name][1], configs))
        #configs = list(filter(lambda c: c[JHIPSTER_FILTERS[feature_name][0]] != JHIPSTER_FILTERS[feature_name][1], configs))
        #print(f"#Filter inverse {feature_name}: {len(configs)}")

    #configs = list(configs)
    if len(configs) == 1:
        return configs[0]
    elif len(configs) == 0:
        print(f"Configuration: {str(configuration)}")
        return None 
    else:
        print(f"#Filtered configs: {len(configs)}")
        print(f"Configuration: {str(configuration)}")
        print(f"Filtered configs: {configs[0]}")
        print(f"Filtered configs: {configs[1]}")
        raise Exception("Error filtering jHipsters configurations.")


def get_jhipster_configurations(feature_name: str, jhipster_configurations: list) -> list:
    return list(filter(lambda c : c[JHIPSTER_FILTERS[feature_name][0]] == JHIPSTER_FILTERS[feature_name][1], jhipster_configurations))


def contains_failures(jhipster_configuration: dict) -> bool:
    """Return True if the jHipster configuration contains errors, False otherwise."""
    return  jhipster_configuration['Build'] == 'KO' or jhipster_configuration['Compile'] == 'KO'


def read_jHipster_configurations() -> list:
    """Read the jHipster configuration from the original .csv file."""
    configs = []
    with open(JHIPSTER_CONFIGS_FILE) as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
        for row in reader:
            configs.append(row)
    return configs


def read_jHipster_feature_model_configurations() -> dict:
    """Read the configurations of the jHipster feature model from the .csv file."""
        # Read the feature model without constraints
    feature_model = FeatureIDEReader(FM_FILE).transform()
    fm = FM(feature_model)
    configs = {}
    with open(JHIPSTER_CONFIGS_FAILURES_FILE) as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',', quotechar='"', skipinitialspace=True)
        for row in reader:
            features = ast.literal_eval(row['Config'])
            config_features = {fm.get_feature_by_name(f): True for f in features}
            selected_features = list(config_features.keys())
            unselected_features = list(set(feature_model.get_features()) - set(selected_features))
            selected_variables = [fm.sat_model.variables[f.name] for f in selected_features]
            unselected_variables = [-fm.sat_model.variables[f.name] for f in unselected_features]
            configuration = FMConfiguration(fm, selected_features, unselected_features, selected_variables, unselected_variables)
            failure = ast.literal_eval(row['Failure'])
            configs[configuration] = failure
            
    return configs


def get_random_sampling(sample_size: int) -> tuple:
    jhipster_configurations = read_jHipster_feature_model_configurations()

    configs_sample = random.sample(list(jhipster_configurations.keys()), sample_size)
    n_positive_evaluations = len([x for x in configs_sample if jhipster_configurations[x]])

    return (configs_sample, n_positive_evaluations)