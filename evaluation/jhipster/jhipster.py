import csv 


JHIPSTER_CONFIGS_FILE = "evaluation/jhipster/jhipster3.6.1-testresults.csv"
FM_FILE = "evaluation/jhipster/fm-3.6.1refined.xml"
CNF_FILE = "evaluation/jhipster/fm-3.6.1refined-cnf.txt"


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
                    'SQL':                          ('databaseType', 'sql', '-'),
                    'Cassandra':                    ('databaseType', 'cassandra', '-'),
                    'MongoDB':                      ('databaseType', 'mongodb', '-'),
                    'DiskBased':                    ('devDatabaseType', 'DiskBased', '-'),
                    'InMemory':                     ('devDatabaseType', 'InMemory', '-'),
                    'PostgreSQLDev':                ('devDatabaseType', 'postgresql', '-'),
                    'MariaDBDev':                   ('devDatabaseType', 'mariadb', '-'),
                    'MySql':                        ('devDatabaseType', 'mysql', '-'),
                    'MySQL':                        ('prodDatabaseType', 'mysql', '-'),
                    'MariaDB':                      ('prodDatabaseType', 'mariadb', '-'),
                    'PostgreSQL':                  ('prodDatabaseType', 'postgresql', '-'),
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
    selected_feature_names = [f.name for f in configuration.get_selected_elements() if not f.is_abstract]
    for feature_name in selected_feature_names:
        if feature_name in JHIPSTER_FILTERS:
            configs = list(filter(lambda c: c[JHIPSTER_FILTERS[feature_name][0]] == JHIPSTER_FILTERS[feature_name][1], configs))
        print(f"#Filter {feature_name}: {len(list(configs))}")
    
    optional_features_not_selected = [f_name for f_name in JHIPSTER_FILTERS.keys() if JHIPSTER_FILTERS[f_name][2] != '-' and f_name not in selected_feature_names]
    for feature_name in optional_features_not_selected:
        #configs = list(filter(lambda c: c[JHIPSTER_FILTERS[feature_name][0]] == JHIPSTER_FILTERS[feature_name][2] or c[JHIPSTER_FILTERS[feature_name][0]] != JHIPSTER_FILTERS[feature_name][1], configs))
        configs = list(filter(lambda c: c[JHIPSTER_FILTERS[feature_name][0]] != JHIPSTER_FILTERS[feature_name][1], configs))
        print(f"#Filter inverse {feature_name}: {len(list(configs))}")

    #configs = list(configs)
    if len(configs) == 1:
        return configs[0]
    elif len(configs) == 0:
        return None 
    else:
        print(f"configs: {configs}")
        raise Exception("Error filtering jHipsters configurations.")


def get_jhipster_configurations(feature_name: str, jhipster_configurations: list) -> list:
    return list(filter(lambda c : c[JHIPSTER_FILTERS[feature_name][0]] == JHIPSTER_FILTERS[feature_name][1], jhipster_configurations))

def contains_failures(jhipster_configuration: dict) -> bool:
    """Return True if the jHipster configuration contains errors, False otherwise."""
    return  jhipster_configuration['Build'] == 'KO' or jhipster_configuration['Compile'] == 'KO'



def read_jHipster_configurations(filepath) -> list:
    """Read the jHipster configuration from the .csv file."""
    configs = []
    with open(filepath) as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
        for row in reader:
            configs.append(row)
    return configs
