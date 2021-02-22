from graphviz import Digraph
from collections import defaultdict

class SearchSpace:

    def __init__(self, initial_state: 'State', max_depth: int = 10):
        self.initial_state = initial_state
        self.max_depth = max_depth
        self.graph = Digraph()
        self.graph.attr('edge', splines='line')
        self.ids = dict()
        self.stats = defaultdict(int)
        self.stats['nof_nodes'] = defaultdict(int)
        self.ni = 1
        self._built(self.initial_state, depth=0)

    def _built(self, state: 'State', parent: 'State' = None, action: 'Action' = None, depth=0):
        if depth <= self.max_depth:
            self.ids[state] = str(self.ni)
            self.ni += 1

            if state.is_terminal():
                self.graph.node(self.ids[state], '', shape='square')
            else:
                self.graph.node(self.ids[state], '')

            self.stats['nof_nodes'][depth] += 1

            if parent:
                self.graph.edge(self.ids[parent], self.ids[state])#, label=action.get_name())

            for action in state.get_actions():
                self._built(action.execute(state), state, action, depth=depth+1)

    def save_graph(self, path: str, format: str, view=True):
        self.graph.render(path, format=format, view=view)
