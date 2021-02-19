from montecarlo4fms.core import State
from famapy.core.models import Configuration


class StateConfiguration(State, Configuration):
    """
    It represents a configuration of a feature model as a state.
    Its successors are any possible selection of features where at least all mandatory decisions are covered, and maybe optional decisions are taken.
    A configuration is terminal if it has not possible successors.
    """
