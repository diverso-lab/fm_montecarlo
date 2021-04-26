from famapy.core.transformations import TextToModel
from montecarlo4fms.aafm.models.feature_model import FeatureModel, Feature, Relation, Constraint
from typing import List
import xml.etree.ElementTree as ET


class FeatureIDEParser(TextToModel):

    @staticmethod
    def get_source_extension() -> str:
        return 'xml'

    def __init__(self, path: str, no_read_constraints: bool = False):
        self._path = path
        self._no_read_constraints = no_read_constraints

    def transform(self) -> FeatureModel:
        return self._read_feature_model(self._path)

    def _read_feature_model(self, filepath: str) -> FeatureModel:
        tree = ET.parse(filepath)
        root = tree.getroot()
        for child in root:
            if child.tag == "struct":
                root = child[0]
                root_feature = Feature(name=root.attrib['name'], relations=[], parent=None)
                #root_feature.add_relation(Relation(parent=None, children=[], card_min=0, card_max=0))   # Relation for the parent.
                (features, children, relations) = self._read_features(root, root_feature)
                features = [root_feature] + features
                fm = FeatureModel(root_feature, [], features, relations)
            elif child.tag == "constraints":
                if not self._no_read_constraints:
                    constraints = self._read_constraints(child, fm)
                    fm.ctcs.extend(constraints)
        return fm

    def _read_features(self, root_tree, parent: Feature) -> (List[Feature], List[Relation]):
        features = []
        children = []
        relations = []
        for child in root_tree:
            if not child.tag == "graphics":
                #children = []
                is_abstract = False
                if "abstract" in child.attrib and child.attrib['abstract']:
                    is_abstract = True
                feature = Feature(name=child.attrib['name'], relations=[], parent=parent, is_abstract=is_abstract)
                #r = Relation(parent=parent, children=[], card_min=0, card_max=0)
                #feature.add_relation(r)   # Relation for the parent.
                features.append(feature)
                children.append(feature)
                #relations.append(r)
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
                    (alt_children, direct_children, children_relations) = self._read_features(child, feature)
                    r = Relation(parent=feature, children=direct_children, card_min=1, card_max=1)
                    feature.add_relation(r)
                    features.extend(alt_children)
                    relations.append(r)
                    relations.extend(children_relations)
                elif child.tag == "or":
                    (or_children, direct_children, children_relations) = self._read_features(child, feature)
                    r = Relation(parent=feature, children=direct_children, card_min=1, card_max=len(direct_children))
                    feature.add_relation(r)
                    features.extend(or_children)
                    relations.append(r)
                    relations.extend(children_relations)
                elif child.tag == "and":
                    (and_children, direct_children, children_relations) = self._read_features(child, feature)
                    features.extend(and_children)
                    relations.extend(children_relations)
        return (features, children, relations)

    def _read_constraints(self, ctcs_root, fm: FeatureModel) -> List[Constraint]:
        n = 1
        constraints = []
        for ctc in ctcs_root:
            index = 0
            if ctc[index].tag == "graphics":
                index += 1
            rule = ctc[index]
            left = rule[0]
            right = rule[1]
            if rule.tag == "imp":
                if right.tag == "not": # A -> !B (Excludes)
                    constraints.append(Constraint(str(n), fm.get_feature_by_name(left.text), fm.get_feature_by_name(right[0].text), 'excludes'))
                else: # A -> B (Requires)
                    constraints.append(Constraint(str(n), fm.get_feature_by_name(left.text), fm.get_feature_by_name(right.text), 'requires'))
            elif rule.tag == "disj":
                if left.tag == "not" and right.tag == "not":    # Excludes
                    constraints.append(Constraint(str(n), fm.get_feature_by_name(left[0].text), fm.get_feature_by_name(right[0].text), 'excludes'))
                elif left.tag == "not": # A -> B (Requires)
                    constraints.append(Constraint(str(n), fm.get_feature_by_name(left[0].text), fm.get_feature_by_name(right.text), 'requires'))
                elif right.tag == "not": # A -> B (Requires)
                    constraints.append(Constraint(str(n), fm.get_feature_by_name(right[0].text), fm.get_feature_by_name(left.text), 'requires'))
            n += 1
        return constraints
