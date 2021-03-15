import sys
sys.path.append('../')
from fm_metamodel.famapy.metamodels.fm_metamodel.models.feature_model import Feature, FeatureModel, Relation, Constraint
from famapy.core.models import Configuration
from montecarlo4fms.models import ConfigurationState
from montecarlo4fms.algorithms import MonteCarloBasic
import cProfile
from typing import List
from montecarlo4fms.utils import FMHelper
from collections import defaultdict


# Feature model input
features_tree = {'Pizza': [(['CheesyCrust'],0,1), (['Topping'],1,1), (['Size'],1,1), (['Dough'],1,1)],
                 'Topping': [(['Salami', 'Ham', 'Mozzarella'],1,3)],
                 'Size': [(['Normal', 'Big'],1,1)],
                 'Dough': [(['Neapolitan', 'Sicilian'],1,1)]
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

    return config

if __name__ == '__main__':
    fm = read_feature_model()
    fm.ctcs.append(Constraint('ctc1', fm.get_feature_by_name('Neapolitan'), fm.get_feature_by_name('Salami'), 'excludes'))
    fm.ctcs.append(Constraint('ctc2', fm.get_feature_by_name('Neapolitan'), fm.get_feature_by_name('Ham'), 'excludes'))
    fm.ctcs.append(Constraint('ctc3', fm.get_feature_by_name('CheesyCrust'), fm.get_feature_by_name('Big'), 'requires'))

    initial_config = read_configuration(fm, ['Pizza', 'Topping', 'Size', 'Dough'])

    fm_helper = FMHelper(fm)
    configurations = fm_helper.get_configurations()
    num = 1
    for c in configurations:
        print(f"config {num}: {c}")
        num += 1

    print(f"#Configurations: {len(configurations)}")
    print(f"Initial config: {initial_config}")
    print(f"is terminal: {initial_config.is_terminal()}")
    print(f"Godel number: {hash(initial_config)}")

    counts = defaultdict(int)
    for f in fm.get_features():
        counts[f] = len([c for c in configurations if f.name in c])

    for f in counts:
        print(f"{f}: {counts[f]}")

    config = montecarlo_basic(fm, initial_config)
    #cProfile.run("montecarlo_basic(fm, initial_config)")
    print(f"Valid?: {fm_helper.is_valid_configuration(config)}")




    ###
    # print(fm)
    # for f in fm.get_features():
    #     print(f"{f} -> parent: {f.get_parent()}")
    #     for r in f.get_relations():
    #         print(f"{f} -> relations: {r}")
