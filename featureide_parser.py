# import sys
# sys.path.append('../')
from famapy_fm.metamodels.fm_metamodel.models import Feature, FeatureModel, Relation, Constraint
#from famapy.core.models import Configuration
from typing import List
import xml.etree.ElementTree as ET

def read_features(root_tree, parent: Feature) -> (List[Feature], List[Relation]):
    features = []
    relations = []
    for child in root_tree:
        children = []
        feature = Feature(child.attrib['name'], [])
        r = Relation(parent=parent, children=[], card_min=0, card_max=0)
        feature.add_relation(r)   # Relation for the parent.
        features.append(feature)
        relations.append(r)
        if root_tree.tag == "and":
            if "mandatory" in child.attrib: # Mandatory feature
                r = Relation(parent=parent, children=[feature], card_min=1, card_max=1)
                parent.add_relation(r)
                relations.append(r)
            else:   # Optional feature
                r = Relation(parent=parent, children=[feature], card_min=0, card_max=1)
                parent.add_relation(r)
                relations.append(r)

        if child.tag == "alt":
            (children, children_relations) = read_features(child, feature)
            r = Relation(parent=feature, children=children, card_min=1, card_max=1)
            feature.add_relation(r)
            features.extend(children)
            relations.append(r)
            relations.extend(children_relations)
        elif child.tag == "or":
            (children, children_relations) = read_features(child, feature)
            r = Relation(parent=feature, children=children, card_min=1, card_max=len(children))
            feature.add_relation(r)
            features.extend(children)
            relations.append(r)
            relations.extend(children_relations)
        elif child.tag == "and":
            (children, children_relations) = read_features(child, feature)
            features.extend(children)
            relations.extend(children_relations)
    return (features, relations)

def read_constraints(ctcs_root, fm: FeatureModel):
    n = 1
    for ctc in ctcs_root:
        rule = ctc[0]
        left = rule[0]
        right = rule[1]
        if rule.tag == "imp":
            if right.tag == "not": # A -> !B (Excludes)
                fm.ctcs.append(Constraint(str(n), fm.get_feature_by_name(left.text), fm.get_feature_by_name(right[0].text), 'excludes'))
            else: # A -> B (Requires)
                fm.ctcs.append(Constraint(str(n), fm.get_feature_by_name(left.text), fm.get_feature_by_name(right.text), 'requires'))
        elif rule.tag == "disj":
            if left.tag == "not" and right.tag == "not":    # Excludes
                fm.ctcs.append(Constraint(str(n), fm.get_feature_by_name(left[0].text), fm.get_feature_by_name(right[0].text), 'excludes'))
            elif left.tag == "not": # A -> B (Requires)
                fm.ctcs.append(Constraint(str(n), fm.get_feature_by_name(left[0].text), fm.get_feature_by_name(right.text), 'requires'))
            elif right.tag == "not": # A -> B (Requires)
                fm.ctcs.append(Constraint(str(n), fm.get_feature_by_name(right[0].text), fm.get_feature_by_name(left.text), 'requires'))
        n += 1

def read_feature_model(filepath: str) -> FeatureModel:
    tree = ET.parse(filepath)
    root = tree.getroot()
    for child in root:
        if child.tag == "struct":
            root = child[0]
            root_feature = Feature(root.attrib['name'], [])
            root_feature.add_relation(Relation(parent=None, children=[], card_min=0, card_max=0))   # Relation for the parent.
            (features, relations) = read_features(root, root_feature)
            features = [root_feature] + features
            fm = FeatureModel(root_feature, [], features, relations)
        if child.tag == "constraints":
            constraints = read_constraints(child, fm)
    return fm


if __name__ == '__main__':
    fm = read_feature_model("input_fms/linux-2.6.33.3basic.xml")
    print(f"#Features: {len(fm.get_features())}")
    print(f"#Constraints: {len(fm.ctcs)}")
