import sys
sys.path.append('../')
from fm_metamodel.famapy.metamodels.fm_metamodel.models.feature_model import Feature, FeatureModel, Relation, Constraint
from famapy.core.models import Configuration
from montecarlo4fms.models import ConfigurationState
import cProfile

from pysat_metamodel.famapy.metamodels.pysat_metamodel.models.pysat_model import PySATModel
from pysat_metamodel.famapy.metamodels.pysat_metamodel.operations.glucose3_products import Glucose3Products
from pysat_metamodel.famapy.metamodels.pysat_metamodel.operations.glucose3_valid import Glucose3Valid
from pysat_metamodel.famapy.metamodels.pysat_metamodel.transformations.fm_to_pysat import FmToPysat

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
    initial_config = read_configuration(fm, [])

    print(f"Initial config: {initial_config}")
    print(f"is terminal: {initial_config.is_terminal()}")
    print(f"Godel number: {hash(initial_config)}")

    # Create a detination metamodel (Pysat for the record)
    sat = PySATModel()

    # Transform the first onto the second
    transform = FmToPysat(fm, sat)
    transform.transform()

    # Create the operation
    valid = Glucose3Valid()

    # Execute the operation . TODO Investigate how t avoid that sat parameter
    valid.execute(sat)

    # Print the result
    print("Is the model valid: " + str(valid.isValid()))

    # Create the operation
    products = Glucose3Products()

    # Execute the operation . TODO Investigate how t avoid that sat parameter
    products.execute(sat)

    # Print the result
    print("The products encoded in the model are: ")
    print(products.getProducts())
