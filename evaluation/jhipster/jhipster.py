import csv 


JHIPSTER_CONFIGS_FILE = "evaluation/jhipster/jhipster3.6.1-testresults.csv"
FM_FILE = "evaluation/jhipster/fm-3.6.1refined.xml"
CNF_FILE = "evaluation/jhipster/fm-3.6.1refined-cnf.txt"


# Mapping of feature names in the FM to filters to apply to the configurations according the values in the .csv.
JHIPSTER_FILTERS = {'Docker':                       lambda c: c['Docker'] == 'TRUE',
                    'MicroserviceApplication':      lambda c: c['applicationType'] == 'microservice',
                    'Monolithic':                   lambda c: c['applicationType'] == 'monolith',
                    'MicroserviceGateway':          lambda c: c['applicationType'] == 'gateway',
                    'UaaServer':                    lambda c: c['applicationType'] == 'uaa',
                    'HTTPSession':                  lambda c: c['authenticationType'] == 'session',
                    'OAuth2':                       lambda c: c['authenticationType'] == 'oauth2',
                    'Uaa':                          lambda c: c['authenticationType'] == 'uaa',
                    'JWT':                          lambda c: c['authenticationType'] == 'jwt',
                    'HazelCast':                    lambda c: c['hibernateCache'] == 'hazelcast',
                    'EhCache':                      lambda c: c['hibernateCache'] == 'ehcache',
                    'ClusteredSession':             lambda c: c['clusteredHttpSession'] == 'hazelcast',
                    'SpringWebSockets':             lambda c: c['websocket'] == 'spring-websocket',
                    'SQL':                          lambda c: c['databaseType'] == 'sql',
                    'Cassandra':                    lambda c: c['databaseType'] == 'cassandra',
                    'MongoDB':                      lambda c: c['databaseType'] == 'mongodb',
                    'DiskBased':                    lambda c: c['devDatabaseType'] == 'DiskBased',
                    'InMemory':                     lambda c: c['devDatabaseType'] == 'InMemory',
                    'PostgreeSQLDev':               lambda c: c['devDatabaseType'] == 'postgresql',
                    'MariaDBDev':                   lambda c: c['devDatabaseType'] == 'mariadb',
                    'MySql':                        lambda c: c['devDatabaseType'] == 'mysql',
                    'MySQL':                        lambda c: c['prodDatabaseType'] == 'mysql',
                    'MariaDB':                      lambda c: c['prodDatabaseType'] == 'mariadb',
                    'PostgreeSQL':                  lambda c: c['prodDatabaseType'] == 'postgresql',
                    'Gradle':                       lambda c: c['buildTool'] == 'gradle',
                    'Maven':                        lambda c: c['buildTool'] == 'maven',
                    'ElasticSearch':                lambda c: c['searchEngine'] == 'elasticsearch',
                    'SocialLogin':                  lambda c: c['enableSocialSignIn'] == 'TRUE',
                    'Libsass':                      lambda c: c['useSass'] == 'TRUE',
                    'InternationalizationSupport':  lambda c: c['enableTranslation'] == 'TRUE'} 


def filter_configuration(configuration: 'FMConfiguration', jhipster_configurations: list) -> dict:
    """Filter the jHipster configurations according to the given configuration and return the dictionary representing the jHipster configuration."""
    configs = list(jhipster_configurations) 
    for feature in configuration.get_selected_features():
        if feature.name in JHIPSTER_FILTERS:
            configs = filter(JHIPSTER_FILTERS[feature.name], configs)
    print(f"#Filtered configs: {len(configs)}")


def contains_errors(jhipster_configuration: dict) -> bool:
    """Return True if the jHipster configuration contains errors, False otherwise."""
    return jhipster_configuration['Log.Build'] != 'OK'


def read_jHipster_configs(filepath) -> list:
    """Read the jHipster configuration from the .csv file."""
    configs = []
    with open(filepath) as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
        for row in reader:
            configs.append(row)
    return configs
