import sys
sys.path.append('../')
from fm_metamodel.famapy.metamodels.fm_metamodel.models.feature_model import Feature, FeatureModel, Relation, Constraint
from famapy.core.models import Configuration
from montecarlo4fms.models import ConfigurationState
import cProfile
from typing import List
from pysat_metamodel.famapy.metamodels.pysat_metamodel.models.pysat_model import PySATModel
from pysat_metamodel.famapy.metamodels.pysat_metamodel.transformations.fm_to_pysat import FmToPysat

from pysat.solvers import Glucose3

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

def read_configuration(feature_model: FeatureModel, config: List['str']) -> Configuration:
    features = feature_model.get_features()
    return ConfigurationState(feature_model, [f for f in features if f.name in config])



if __name__ == '__main__':
    fm = read_feature_model()
    fm.ctcs.append(Constraint('ctc1', fm.get_feature_by_name('B11'), fm.get_feature_by_name('C2'), 'requires'))
    fm.ctcs.append(Constraint('ctc2', fm.get_feature_by_name('E111'), fm.get_feature_by_name('E2'), 'excludes'))
    fm.ctcs.append(Constraint('ctc3', fm.get_feature_by_name('C2'), fm.get_feature_by_name('F1'), 'requires'))

    initial_config = read_configuration(fm, ['A', 'B', 'B1', 'B', 'E', 'E1', 'B12'])

    print(f"Initial config: {initial_config}")
    print(f"is terminal: {initial_config.is_terminal()}")
    print(f"Godel number: {hash(initial_config)}")

    # Create a detination metamodel (Pysat for the record)
    sat = PySATModel()

    # Transform the first onto the second
    transform = FmToPysat(fm)
    cnf_model = transform.transform()
    print(cnf_model)

    ###################################
    g = Glucose3()
    for clause in cnf_model.cnf:  # AC es conjunto de conjuntos
        g.add_clause(clause)  # añadimos la constraint
    result = g.solve()
    print(f"Valid: {result}")
    print(f"Valid: {g.solve()}")
    print(f"Valid: {g.solve(assumptions=[1, 2, 3, 4, 14, 15, -16])}") # para chequear configuraciones parciales.


    ###################################
    products = []
    for solutions in g.enum_models():
        product = list()
        for variable in solutions:
            if variable > 0:  # This feature should appear in the product
                product.append(cnf_model.features.get(variable))
        products.append(product)
    print(f"#Configurations: {len(products)}")

    ###################################
    g = Glucose3()
    for clause in cnf_model.cnf:  # AC es conjunto de conjuntos
        g.add_clause(clause)  # añadimos la constraint

    for f in cnf_model.features.items():
        print(f)

    core = g.get_core() # para chequear inconsistencias.
    print(f"Core: {core}")

    # Chequear configuraciones válidas.
    for f in fm.get_features():
        literal = 1 if f in initial_config.elements else -1
        clause = [x[0]*literal for x in cnf_model.features.items() if x[1] == f.name]
        if clause:
            g.add_clause(clause)

    for c in cnf_model.cnf:
        print(type(c), c)

    print(f"Valid config: {g.solve()}")
