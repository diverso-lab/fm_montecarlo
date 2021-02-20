from graphviz import Digraph


class SearchSpace:

    def __init__(self, initial_state: 'State', max_depth: int = 10):
        self.initial_state = initial_state
        self.max_depth = max_depth
        self.graph = Digraph()
        self.graph.attr('edge', splines='line')
        self.ids = dict()
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

            if parent:
                self.graph.edge(self.ids[parent], self.ids[state])#, label=action.get_name())

            for action in state.get_actions():
                self._built(state.transition_function(action), state, action, depth=depth+1)

    def save_graph(self, path: str, format: str):
        self.graph.render(path, format=format, view=True)
