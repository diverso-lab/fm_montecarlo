import sys
from xml.etree import ElementTree

from famapy.core.transformations import TextToModel
from famapy.core.exceptions import DuplicatedFeature
from famapy.metamodels.fm_metamodel.models.feature_model import Feature, FeatureModel, Relation, Constraint


class XMLTransformation(TextToModel):

    @staticmethod
    def get_source_extension() -> str:
        return 'xml'

    def __init__(self, path):
        self.path = path
        # TODO: add empty FeatureModel
        # self.model = FeatureModel(feature, [])
        self.name_feature = {}

    def transform(self):
        rootcounter = 1
        tree = ElementTree.parse(self.path)
        xml_root = tree.getroot()
        # iterate over child of the xml root element
        for child in xml_root:
            if child.tag.casefold() == 'feature':
                rootcounter += 1
                root = self.parse_feature(child)
                fm = FeatureModel(root,[])
            elif child.tag.casefold() == 'excludes' or child.tag.casefold() == 'requires':
                ctc=self.parse_ctc(child)
                fm.ctcs.append(ctc)
            else:
                print("This XML contains non supported elements", file=sys.stderr)

        return fm

    def parse_ctc(self,element)->Constraint:

        name=element.attrib.get('name')
        ctc_type=element.tag.casefold()
        origin=self.name_feature[element.attrib.get('feature')]

        if ctc_type == 'excludes':
            destination=self.name_feature[element.attrib.get('excludes')]
        elif ctc_type == 'requires':
            destination=self.name_feature[element.attrib.get('requires')]

        return Constraint(name,origin,destination,ctc_type)

    def parse_feature(self, element) -> Feature:
        name = element.attrib.get('name')


        feature = Feature(name, [])

        if name in self.name_feature:
            print("This XML contains duplicated feature names", file=sys.stderr)
            raise DuplicatedFeature
        else:
            self.name_feature[name]=feature

        for child in element:
            if child.tag.casefold() == 'setrelation' or child.tag.casefold() == 'binaryrelation':
                relation = self.parse_relation(child)
                relation.parent = feature
                feature.relations.append(relation)

     
        return feature

    def parse_relation(self, element) -> Relation:
        r = Relation(parent=None, children=[], card_min=0, card_max=0)

        if element.tag.casefold() == 'binaryrelation':
            num_solitary_features = 0

            for child in element:
                if child.tag.casefold() == 'solitaryfeature':
                    num_solitary_features += 1
                    f = self.parse_feature(child)
                    r.children.append(f)
                elif child.tag.casefold() == 'cardinality':
                    r.card_min = int(child.attrib.get('min'))
                    r.card_max = int(child.attrib.get('max'))
                else:
                    print("This XML contains non supported elements", file=sys.stderr)

        elif element.tag.casefold() == 'setrelation':
            for child in element:
                if child.tag.casefold() == 'groupedfeature':
                    f = self.parse_feature(child)
                    r.children.append(f)
                elif child.tag.casefold() == 'cardinality':
                    r.card_min = int(child.attrib.get('min'))
                    r.card_max = int(child.attrib.get('max'))
                else:
                    print("This XML contains non supported elements", file=sys.stderr)

        return r
