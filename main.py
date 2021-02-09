import sys
sys.path.append('../')
from fm_metamodel.famapy.metamodels.fm_metamodel.models.feature_model import Feature, FeatureModel, Relation, Constraint
from famapy.core.models import Configuration
from montecarlo4fms.models import ConfigurationState
from montecarlo4fms.algorithms import MonteCarloBasic
import cProfile
from typing import List
from montecarlo4fms.utils import FMHelper
from montecarlo4fms.utils import PerformanceModel
from montecarlo4fms.algorithms import MonteCarloTreeSearch

# Feature model input
# features_tree = {'A': [(['B'],1,1), (['C'],0,1), (['D'],0,1), (['E'],1,1), (['F'],0,1)],
#                  'B': [(['B1'],1,1)],
#                  'B1': [(['B11', 'B12'],1,2)],
#                  'C': [(['C1', 'C2'],1,1)],
#                  'D': [(['D1'],1,1)],
#                  'D1': [(['D11', 'D12', 'D13'],1,3)],
#                  'E': [(['E1'],1,1), (['E2'],0,1)],
#                  'E1': [(['E11'],0,1)],
#                  'E11': [(['E111', 'E112', 'E113'],1,1)],
#                  'F': [(['F1'],0,1)],
#                  'F1': [(['F12'],1,1), (['F13'],1,1)],
#                  'F12': [(['F121'],0,1)],
#                  'F13': [(['F131'],0,1)]
#                  }
features_tree = {'FQAs': [(['Logging'],1,1)],
                 'Logging': [(['UsageContext'],1,1), (['Output'],1,1), (['Framework'],1,1)],
                 'UsageContext': [(['FileSize'],1,1)],
                 'Output': [(['console', 'file'],1,1)],
                 'Framework': [(['java.util.logging', 'Log4J', 'LogBack classic', 'Simple implementation'],1,1)],
                 'FileSize': [([str(10**n) for n in range(0,10)],1,1)]
                 }


def read_feature_model() -> FeatureModel:
    root = None
    features = []

    for f in features_tree:
        feature = next((x for x in features if x.name == f), None)
        if not feature:
            feature = Feature(f, [])
        if not root:
            root = feature
            root.add_relation(Relation(parent=None, children=[], card_min=0, card_max=0))   # Relation for the parent.

        for relation in features_tree[f]:
            children = [Feature(c, []) for c in relation[0]]
            relation = Relation(parent=feature, children=children, card_min=relation[1], card_max=relation[2])
            feature.add_relation(relation)
            for child in children: # Add relation for the parent
                r = Relation(parent=feature, children=[], card_min=0, card_max=0)
                child.add_relation(r)
            features.extend(children)

    return FeatureModel(root, [])

def read_configuration(feature_model: FeatureModel, config: List['str']) -> Configuration:
    features = feature_model.get_features()
    return ConfigurationState(FMHelper(feature_model), [f for f in features if f.name in config])

def montecarlo_basic(fm, config):
    print("-----MonteCarlo-----")
    mc = MonteCarloBasic(1000)
    config = initial_config
    print(f"Config {hash(config)}: {config} -> reward: {config.reward()}")
    while not config.is_terminal():
        config = mc.choose(config)
        mc.print_MC_values()
        print(f"Config {hash(config)}: {config} -> reward: {config.reward()}")

def montecarlo_treesearch(fm, config):
    print("-----MonteCarlo-----")
    mc = MonteCarloTreeSearch(100)
    config = initial_config
    n_iteration = 1
    while not config.is_terminal():
        print(f"Iteration: {n_iteration}")
        n_iteration += 1
        print(f"Current config {hash(config)}: {config} -> reward: {config.reward()}")
        for s in config.find_successors():
            print(f"Successor: {s}")

        config = mc.choose(config)
        mc.print_MC_values()
        print(f"Best successor {hash(config)}: {config} -> reward: {config.reward()}")


if __name__ == '__main__':
    fm = read_feature_model()
    #fm.ctcs.append(Constraint('ctc1', fm.get_feature_by_name('B11'), fm.get_feature_by_name('C2'), 'requires'))
    #fm.ctcs.append(Constraint('ctc2', fm.get_feature_by_name('E111'), fm.get_feature_by_name('E2'), 'excludes'))
    #fm.ctcs.append(Constraint('ctc3', fm.get_feature_by_name('C2'), fm.get_feature_by_name('F1'), 'requires'))

    initial_config = read_configuration(fm, [])

    print(fm)
    for f in fm.get_features():
        print(f"{f} -> parent: {f.get_parent()}")
        for r in f.get_relations():
            print(f"{f} -> relations: {r}")

    print(f"Initial config: {initial_config}")
    print(f"is terminal: {initial_config.is_terminal()}")
    print(f"Godel number: {hash(initial_config)}")

    # pm = PerformanceModel(fm)
    # pm.load_configurations_from_csv('logging-performance.csv', ['Framework', 'Message Size (b)', 'Output'], 'Computational Time (s)')
    # m = pm.get_model()
    # for c in m:
    #     print(f"{c.elements}: {m[c]}")
    #montecarlo_basic(fm, initial_config)
    montecarlo_treesearch(fm, initial_config)
    #cProfile.run("montecarlo_basic(fm, initial_config)")




    ###
    # print(fm)
    # for f in fm.get_features():
    #     print(f"{f} -> parent: {f.get_parent()}")
    #     for r in f.get_relations():
    #         print(f"{f} -> relations: {r}")
