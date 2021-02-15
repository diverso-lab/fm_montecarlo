import sys
sys.path.append('../')
from fm_metamodel.famapy.metamodels.fm_metamodel.models.feature_model import Feature, FeatureModel, Relation, Constraint
from typing import List
import xml.etree.ElementTree as ET
from montecarlo4fms.utils import FMHelper

# def read_features(lines: List[str], parent: Feature, children_features:list, card_min: int, card_max: int, current_tab: int) -> List[Feature]:
#     features = []
#     if lines:
#         line = lines.pop(0)
#         if line:
#             tabs = line.split("\t").count("")
#
#
#             if "mandatory" in line:
#                 current_tab = tabs
#                 while tabs >= current_tab:
#                     children = read_features(lines, parent=parent, children_features=[], card_min=1, card_max=1, current_tab=tabs)
#                     for c in children:
#                         parent.add_relation(Relation(parent=parent, children=[c], card_min=1, card_max=1))
#             elif "optional" in line:
#                 children = read_features(lines, parent=parent, children_features=[], card_min=0, card_max=1, current_tab=tabs)
#                 for c in children:
#                     parent.add_relation(Relation(parent=parent, children=[c], card_min=0, card_max=1))
#             elif "alternative" in line:
#
#
#                 children = read_features(lines, parent=parent, children_features=[], card_min=1, card_max=1, current_tab=tabs)
#                 parent.add_relation(Relation(parent=parent, children=children, card_min=1, card_max=1))
#                 return read_features(parent, children_features, card_min, card_max, tabs)
#             elif "or" in line:
#                 children = read_features(lines, parent=parent, children_features=[], card_min=1, card_max=1, current_tab=tabs)
#                 parent.add_relation(Relation(parent=parent, children=children, card_min=0, card_max=len(children)))
#             else:
#                 feature_name = line.split()[0]
#                 feature = Feature(feature_name, [])
#                 feature.add_relation(Relation(parent=parent, children=[], card_min=0, card_max=0)) # Relation for the parent
#                 if tabs > current_tab:
#                     children_features.append(feature)
#                     return read_features(parent, [feature], card_min, card_max, tabs)
#                 elif tabs == current_tab:
#                     children_features.append(feature)
#                     return read_features(parent, children_features, card_min, card_max, tabs)
#                 else:
#                     return children_features

# def read_feature_model(filepath: str) -> FeatureModel:
#     root = None
#     features = []
#     card_min = 0
#     card_max = 0
#
#     with open(filepath) as file:
#         lines = file.readlines()
#         line = lines.pop(0)
#         while "features" not in line and lines: # Look for the root
#             line = lines.pop(0)
#         if lines:
#             root_name = lines.pop(0).split()[0]
#             root_feature = Feature(root_name, [])
#             root_feature.add_relation(Relation(parent=None, children=[], card_min=0, card_max=0))   # Relation for the parent.
#             read_features(lines, parent=root_feature, children=[], card_min=0, card_max=0, current_tab=0)

    #
    # for f in features_tree:
    #     feature = next((x for x in features if x.name == f), None)
    #     if not feature:
    #         feature = Feature(f, [])
    #     if not root:
    #         root = feature
    #         root.add_relation(Relation(parent=None, children=[], card_min=0, card_max=0))   # Relation for the parent.
    #
    #     for relation in features_tree[f]:
    #         children = [Feature(c, []) for c in relation[0]]
    #         relation = Relation(parent=feature, children=children, card_min=relation[1], card_max=relation[2])
    #         feature.add_relation(relation)
    #         for child in children: # Add relation for the parent
    #             r = Relation(parent=feature, children=[], card_min=0, card_max=0)
    #             child.add_relation(r)
    #         features.extend(children)

    # return FeatureModel(root, [])

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
    fm_helper = FMHelper(fm)
    n = 1
    for ctc in ctcs_root:
        rule = ctc[0]
        left = rule[0]
        right = rule[1]
        if rule.tag == "imp":
            if right.tag == "not": # A -> !B (Excludes)
                fm.ctcs.append(Constraint(str(n), fm_helper.features_by_name[left.text], fm_helper.features_by_name[right[0].text], 'excludes'))
            else: # A -> B (Requires)
                fm.ctcs.append(Constraint(str(n), fm_helper.features_by_name[left.text], fm_helper.features_by_name[right.text], 'requires'))
        elif rule.tag == "disj":
            if left.tag == "not" and right.tag == "not":    # Excludes
                fm.ctcs.append(Constraint(str(n), fm_helper.features_by_name[left[0].text], fm_helper.features_by_name[right[0].text], 'excludes'))
            elif left.tag == "not": # A -> B (Requires)
                fm.ctcs.append(Constraint(str(n), fm_helper.features_by_name[left[0].text], fm_helper.features_by_name[right.text], 'requires'))
            elif right.tag == "not": # A -> B (Requires)
                fm.ctcs.append(Constraint(str(n), fm_helper.features_by_name[right[0].text], fm_helper.features_by_name[left.text], 'requires'))
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
