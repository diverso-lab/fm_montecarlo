from graphviz import Digraph
from collections import defaultdict

class SearchSpace:

    def __init__(self, initial_state: 'State', max_depth: float = float("Inf")):
        self.initial_state = initial_state
        self.max_depth = max_depth
        self.graph = Digraph()
        self.graph.attr('edge', splines='line')
        self.ids = dict()
        self.stats = defaultdict(int)
        self.stats['nof_nodes'] = defaultdict(int)
        #self._built()
        self._built_improve()

    def _built(self):
        depth = 0
        nof_nodes = 0
        states = [self.initial_state]
        parents = {self.initial_state: None}
        actions = {self.initial_state: None}
        while depth <= self.max_depth and states:
            if not self.stats['nof_nodes'][depth]:
                self.stats['nof_nodes'][depth] = len(states)

            children = []
            for s in states:
                self.ids[s] = str(nof_nodes)
                nof_nodes += 1
                self._draw_node(s, parents[s], actions[s])

                if not s.is_terminal():
                    for action in s.get_actions():
                        child = action.execute(s)
                        children.append(child)
                        parents[child] = s
                        actions[child] = action

            print(f"Depth {depth}: {self.stats['nof_nodes'][depth]} nodes / total: {nof_nodes}")
            depth += 1
            states = children

    def _built_improve(self):
        depth = 0
        nof_nodes = 0
        states = [self.initial_state]
        while depth <= self.max_depth and states:
            if not self.stats['nof_nodes'][depth]:
                self.stats['nof_nodes'][depth] = len(states)

            children = []
            for s in states:
                nof_nodes += 1

                if not s.is_terminal():
                    children.extend(s.find_successors())

            print(f"Depth {depth}: {self.stats['nof_nodes'][depth]} nodes / total: {nof_nodes}")
            depth += 1
            states = children

    def _draw_node(self, state: 'State', parent: 'State', action: 'Action'):
        #print(f"action: {action} -> state: {[str(f) for f in state.configuration.elements]}")
        if state.is_terminal():
            self.graph.node(self.ids[state], '', shape='square')
        else:
            self.graph.node(self.ids[state], '')

        if parent:
            if action:
                self.graph.edge(self.ids[parent], self.ids[state], label=str(action))
            else:
                self.graph.edge(self.ids[parent], self.ids[state])

    def save_graph(self, path: str, format: str, view=True):
        self.graph.render(path, format=format, view=view)
