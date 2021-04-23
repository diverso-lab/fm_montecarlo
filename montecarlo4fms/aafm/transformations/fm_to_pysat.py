import sys

from famapy.core.models import VariabilityModel
from famapy.core.transformations import ModelToModel
from famapy.metamodels.pysat_metamodel.models.pysat_model import PySATModel


class FmToPysat(ModelToModel):
    @staticmethod
    def get_source_extension():
        return 'fm'

    @staticmethod
    def get_destination_extension():
        return 'pysat'

    def __init__(self, source_model: VariabilityModel):
        self.source_model = source_model
        self.counter = 1
        self.destination_model = PySATModel()
        self.cnf = self.destination_model.cnf

    def add_feature(self, feature):
        if feature.name not in self.destination_model.variables.keys():
            self.destination_model.variables[feature.name] = self.counter
            self.destination_model.features[self.counter] = feature.name
            self.counter += 1

    def add_root(self, feature):
        self.cnf.append([self.destination_model.variables.get(feature.name)])

    def add_relation(self, relation):
        if (relation.is_mandatory()):
            self.cnf.append([
                -1 * self.destination_model.variables.get(relation.parent.name),
                self.destination_model.variables.get(relation.children[0].name)])
            self.cnf.append([
                -1 * self.destination_model.variables.get(relation.children[0].name),
                self.destination_model.variables.get(relation.parent.name)])

        elif (relation.is_optional()):
            self.cnf.append([
                -1 * self.destination_model.variables.get(relation.children[0].name),
                self.destination_model.variables.get(relation.parent.name)])

        elif (relation.is_or()):  # this is a 1 to n relatinship with multiple childs
            # add the first cnf child1 or child2 or ... or childN or no parent)
            alt_cnf = [-1 * self.destination_model.variables.get(relation.parent.name)]  # first elem of the constraint
            for child in relation.children:
                alt_cnf.append(self.destination_model.variables.get(child.name))
            self.cnf.append(alt_cnf)

            for child in relation.children:
                self.cnf.append([
                    -1 * self.destination_model.variables.get(child.name),
                    self.destination_model.variables.get(relation.parent.name)])

        elif (relation.is_alternative()):  # this is a 1 to 1 relatinship with multiple childs
            # add the first cnf child1 or child2 or ... or childN or no parent)
            alt_cnf = [-1 * self.destination_model.variables.get(relation.parent.name)]  # first elem of the constraint
            for child in relation.children:
                alt_cnf.append(self.destination_model.variables.get(child.name))
            self.cnf.append(alt_cnf)

            for i in range(len(relation.children)):
                for j in range(i+1, len(relation.children)):
                    if i != j:
                        self.cnf.append([
                            -1 * self.destination_model.variables.get(relation.children[i].name),
                            -1*self.destination_model.variables.get(relation.children[j].name)])
                self.cnf.append([-1*self.destination_model.variables.get(relation.children[i].name),self.destination_model.variables.get(relation.parent.name)])

        else:  # This is a m to n relationship
            pass
            # from itertools import combinations
            # index = relation.card_min
            # _dnf=[]
            # while index <= relation.card_max:
            #     _combinations=list(combinations(relation.children,index))
            #     for _combination in _combinations:
            #         clause=[]
            #         for feature in _combination:
            #             clause.append(self.destination_model.variables.get(feature.name))
            #         _dnf.append(clause)
            #     index += 1
            # print(_dnf)
            # print("fatal error. N to M relationships are not yet supported in PySAT", file=sys.stderr)
            # raise NotImplementedError

    def add_constraint(self, ctc):
        dest = self.destination_model.variables.get(ctc.destination.name)
        orig = self.destination_model.variables.get(ctc.origin.name)
        if ctc.ctc_type == 'requires':
            self.cnf.append([-orig, dest])

        elif ctc.ctc_type == 'excludes':
            self.cnf.append([-orig, -dest])

    def transform(self):
        if self.source_model.root:
            for feature in self.source_model.get_features():
                self.add_feature(feature)

            self.add_root(self.source_model.root)

            for relation in self.source_model.get_relations():
                self.add_relation(relation)

            for constraint in self.source_model.get_constraints():
                self.add_constraint(constraint)

        return self.destination_model
