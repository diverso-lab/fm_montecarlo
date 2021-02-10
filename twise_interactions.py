import sys
sys.path.append('../')
from fm_metamodel.famapy.metamodels.fm_metamodel.models import Feature, FeatureModel, Relation, Constraint, FMConfiguration
from montecarlo4fms.utils import FMHelper
import itertools


features_tree = {'GraphLibrary': [(['Edges'],1,1), (['Algorithms'],0,1)],
                 'Edges': [(['Directed', 'Undirected'],1,1)],
                 'Algorithms': [(['Path', 'Cycle'],1,2)]
                 }

def powerset(s):
    x = len(s)
    masks = [1 << i for i in range(x)]
    for i in range(1 << x):
        yield [ss for mask, ss in zip(masks, s) if i & mask]


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

if __name__ == '__main__':
    t = 2
    fm = read_feature_model()
    fm.ctcs.append(Constraint('ctc1', fm.get_feature_by_name('Cycle'), fm.get_feature_by_name('Directed'), 'requires'))
    fm_helper = FMHelper(fm)

    features = fm.get_features()
    core_features = fm_helper.get_core_features()
    print(f"Core-Features = {core_features}")

    configs = fm_helper.get_configurations()
    print(f"#Configurations: {len(configs)}")

    combis = itertools.combinations(features, t)
    interactions = {x : powerset(x) for x in combis}

    nof_total_interactions = len(interactions)*t**2
    print(f"Total number of interactions: {nof_total_interactions}")
    #valid_interactions = {i : core_features.intersection(list(interactions[i])) for i in interactions}

    valid_interactions = dict()
    nof_interactions = 0
    for i in interactions:
        # Detecting invalid combinations
        # Remove those invalid interactions due to they contain core-features or due to cross-tree constraints
        core_features_interactions = core_features.intersection(set(i))
        valid_interactions[i] = [x for x in interactions[i] if core_features_interactions.issubset(x) and fm_helper.is_valid_partial_selection(x, set(i).difference(x))]
        nof_interactions += len(valid_interactions[i])
        #print(f"{i}: {list(valid_interactions[i])}")

    print(f"Reduced number of interactions: {nof_interactions} ({nof_total_interactions - nof_interactions} removed)")

    # reduced_valid_interactions = dict()
    # nof_reduced_interactions = 0
    # for i in valid_interactions:
    #     partial_configs = set()
    #     for x in valid_interactions[i]:
    #         config = FMConfiguration([fm.get_feature_by_name(f) for f in x])
    #         if fm_helper.is_valid_partial_configuration(config):
    #             partial_configs.add(x)
    #     reduced_valid_interactions[i] = partial_configs
    #     nof_reduced_interactions += len(partial_configs)

    # print(f"Reduced number of valid interactions: {nof_reduced_interactions} ({nof_interactions - nof_reduced_interactions} removed)")
    for i in valid_interactions:
        print(f"{i}: {list(valid_interactions[i])}")
