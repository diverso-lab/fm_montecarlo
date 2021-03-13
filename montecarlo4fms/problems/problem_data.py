
class ProblemData:

    def __init__(self, feature_model: 'FeatureModel', aafms: 'AAFMsHelper', actions: 'Actions' = None):
        self.fm = feature_model
        self.aafms = aafms
        self.actions = actions
