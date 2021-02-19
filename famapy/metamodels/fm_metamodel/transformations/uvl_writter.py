from typing import List

from famapy.core.transformations import ModelToText
from famapy.core.models import VariabilityModel

from famapy.metamodels.fm_metamodel.models import FeatureModel, Feature, Relation, Constraint


class UVLWritter(ModelToText):

    @staticmethod
    def get_destination_extension() -> str:
        return "uvl"

    def __init__(self, path: str, source_model: VariabilityModel) -> None:
        self._path = path
        self._source_model = source_model

    def transform(self) -> str:
        model = self._write_uvl_model(self._source_model)
        with open(self._path, "w+") as file:
            file.write(model)
        return model

    def _write_uvl_model(self, model: FeatureModel) -> str:
        # empty model
        if not model or not model.root:
            return ""
        # feature model and root feature
        text = "namespace " + model.root.name + "\n\n"
        text += "features\n"
        #text += "\t" + model.root.name + "{abstract}\n"
        # features
        text += self._transverse_feature_tree(feature=model.root, tabs=1)
        # constraints
        if model.ctcs:
            text += "\nconstraints\n"
            text += self._tranverse_constraints(model.ctcs)
        return text

    def _transverse_feature_tree(self, feature: Feature, tabs: int) -> str:
        indentation = "\t" * tabs

        optional_relations = [r for r in feature.get_relations() if r.is_optional()]
        mandatory_relations = [r for r in feature.get_relations() if r.is_mandatory()]
        or_relations = [r for r in feature.get_relations() if r.is_or()]
        and_relations = [r for r in feature.get_relations() if r.is_alternative()]

        text = ""
        if not feature.get_parent():    # root feature
            text += indentation + feature.name + " {abstract}\n"
        else:
            text += indentation + feature.name + "\n"

        tabs += 1
        indentation = "\t" * tabs
        if mandatory_relations:
            text += indentation + "mandatory\n"
            for r in mandatory_relations:
                #text += indentation + feature.name + "\n"
                for child in r.children:
                    text += self._transverse_feature_tree(child, tabs+1)

        if optional_relations:
            text += indentation + "optional\n"
            for r in optional_relations:
                #text += indentation + feature.name + "\n"
                for child in r.children:
                    text += self._transverse_feature_tree(child, tabs+1)

        if or_relations:
            text += indentation + "or\n"
            for child in or_relations[0].children:
                text += self._transverse_feature_tree(child, tabs+1)

        if and_relations:
            text += indentation + "alternative\n"
            for child in and_relations[0].children:
                text += self._transverse_feature_tree(child, tabs+1)

        return text

    def _tranverse_constraints(self, ctcs: List[Constraint]) -> str:
        text = ""
        for c in ctcs:
            if ctc_type == 'requires':
                text += "\t" + c.origin.name + " => " + c.destination.name + "\n"
            elif ctc_type == 'excludes':
                text += "\t" + c.origin.name + " => !" + c.destination.name + "\n"
        return text
