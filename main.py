import sys
sys.path.append('../')
from fm_metamodel.famapy.metamodels.fm_metamodel.models.feature_model import Feature, FeatureModel, Relation, Constraint
from famapy.core.models import Configuration
from montecarlo4fms.models import ConfigurationState
from montecarlo4fms.algorithms import MonteCarloBasic


# Feature model input
features_tree = {'A': [(['B'],1,1), (['C'],0,1), (['D'],0,1), (['E'],1,1), (['F'],0,1)],
                 'B': [(['B1'],1,1)],
                 'B1': [(['B11', 'B12'],1,2)],
                 'C': [(['C1', 'C2'],1,1)],
                 'D': [(['D1'],1,1)],
                 'D1': [(['D11', 'D12', 'D13'],1,3)],
                 'E': [(['E1'],1,1), (['E2'],0,1)],
                 'E1': [(['E11'],0,1)],
                 'E11': [(['E111', 'E112', 'E113'],1,1)],
                 'F': [(['F1'],0,1)],
                 'F1': [(['F12'],1,1), (['F13'],1,1)],
                 'F12': [(['F121'],0,1)],
                 'F13': [(['F131'],0,1)]
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

def read_configuration(feature_model: FeatureModel, config: list['str']) -> Configuration:
    features = feature_model.get_features()
    return ConfigurationState(feature_model, [f for f in features if f.name in config])


if __name__ == '__main__':
    fm = read_feature_model()
    initial_config = read_configuration(fm, ['A', 'B', 'B1', 'E', 'E1'])

    print(f"Initial config: {initial_config}")
    print(f"is terminal: {initial_config.is_terminal()}")
    print(f"Godel number: {hash(initial_config)}")

    print("-----MonteCarlo-----")
    mc = MonteCarloBasic(1000)
    #initial_config = read_configuration(fm, ['A'])
    mc_successor = mc.choose(initial_config)
    print(f"Best successor: {mc_successor}")
    mc_successor2 = mc.choose(mc_successor)
    print(f"Best successor 2: {mc_successor2}")

    print(f"Original config: {initial_config}")

    ###
    # print(fm)
    # for f in fm.get_features():
    #     print(f"{f} -> parent: {f.get_parent()}")
    #     for r in f.get_relations():
    #         print(f"{f} -> relations: {r}")
