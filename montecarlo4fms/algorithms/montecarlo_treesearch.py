from abc import abstractmethod
from collections import defaultdict
from typing import List

from montecarlo4fms.algorithms import MonteCarlo
from montecarlo4fms.models import State


class MonteCarloTreeSearch(MonteCarlo):
    """
    Monte Carlo Tree Search (MCTS) strategy.
    A search tree is built in an incremental and assymetric manner.
    For each iteration of the algorithm, a tree policy is used to find the most urgent node of the current tree.
    It uses uniform random choices as the default policy for simulations.
    """

    def __init__(self, stopping_condition: 'StoppingCondition', selection_criteria: 'SelectionCriteria'):
        super().__init__(stopping_condition, selection_criteria)
        self.initialize()
        self.states_evaluated = dict()         # terminal state -> reward value
        self.terminal_nodes_visits = 0
        self.nof_reward_function_calls = 0

    def initialize(self):
        super().initialize()
        self.Q = defaultdict(int)   # total reward of each state
        self.N = defaultdict(int)   # total visit count of each state
        self.tree = dict()          # the MC tree as a dict of state -> children

    def do_rollout(self, state: State):
        """Make the search tree one layer better (train for one iteration)."""
        path = self.select(state)
        leaf = path[-1]
        self.expand(leaf)
        reward = self.simulate(leaf)
        self.backpropagate(path, reward)

    def choose(self, state: State) -> State:
        if state not in self.tree:
            return state.find_random_successor()
        return self.selection_criteria.best_child(state, self.tree[state], self.Q, self.N)

    def score(self, state: State) -> float:
        return self.selection_criteria.score(state, self.Q, self.N)

    def select(self, state: State) -> List[State]:
        """
        Step 1: Selection.
        Find an expandable/unexplored child node of `state`.
        A node is expandable if it represents a nonterminal state and has unvisited.
        The tree policy is applied recursively until a leaf node is reached.
        Return the list of nodes visited.
        """
        path = [state]
        while state in self.tree and self.tree[state]:  # while state is neither explored nor terminal (if the node has children in the tree means that is not terminal)
            unexplored = self.tree[state] - self.tree.keys()
            if unexplored:  # the node is not fully expanded
                s = unexplored.pop()
                path.append(s)
                return path
            state = self.best_child(state)
            path.append(state)
        return path

    @abstractmethod
    def best_child(self, state: State) -> State:
        """Select the best child of state in the search tree according to a policy tree."""
        pass

    def expand(self, state: State):
        """
        Step 2: Expansion.
        Update the tree with the children of 'state'.
        """
        if not state in self.tree:
            self.tree[state] = state.find_successors()

    def simulate(self, state: State) -> float:
        """
        Step 3. Simulation.
        A simulation is rolled out using the default policy (uniform random choices).
        Return the simulation's reward (i.e., reward of the terminal state).
        """
        while not state.is_terminal():
            state = state.find_random_successor()
        z = state.reward()
        self.states_evaluated[state] = z
        self.nof_reward_function_calls += 1
        self.terminal_nodes_visits += 1
        # if state in self.states_evaluated:
        #     z = self.states_evaluated[state]
        # else:
        #     z = state.reward()
        #     self.states_evaluated[state] = z 
        #     self.nof_reward_function_calls += 1
        # self.terminal_nodes_visits += 1
        return z

    def backpropagate(self, path, reward):
        """
        Step 4. Backpropagation.
        Send the reward back up to the visited nodes in the tree.
        """
        for state in reversed(path):
            self.N[state] += 1
            self.Q[state] += reward

    def print_MC_values(self, state: State):
        print("----------MCTS stats----------")
        print(f"MonteCarloTreeSearch values:")
        if state in self.tree:
            for s in self.tree[state]:
                print(f"//MC values for state: {str(s)} -> {self.Q[s]}/{self.N[s]} = {self.score(s)}")
            print(f"#Decisions: {len(self.tree[state])}")
            #if len(self.tree[state]) > 0:
                #print(f"Best decision: {self.choose(state)}")
        else:
            print(f"State not found in tree search: {state}")
        print(f"Total nodes in the tree search: {len(self.tree)}")
        print("------------------------------")

    def print_MC_search_tree(self):
        with open("MCTS-treesearch.txt", 'w+') as file:
            file.write("----------MCTS search tree stats----------\n")
            for state in self.tree:
                file.write(f"+MC values for state: {str(state)} -> {self.Q[state]}/{self.N[state]} = {self.score(state)}\n")
                file.write(f" |-children: {len(self.tree[state])}\n")
                file.write(f" |-Nodes in the tree search: {len(self.tree)}\n")
                for s in self.tree[state]:
                    file.write(f" |--MC values for state: {str(s)} -> {self.Q[s]}/{self.N[s]} = {self.score(s)}\n")
            file.write(f"#Total nodes in the tree search: {len(self.tree)}\n")
            file.write("------------------------------\n")
    
    def print_heat_map(self, feature_model):
        feature_rewards = defaultdict(int)
        feature_visits = defaultdict(int)
        
        for state in self.tree:
            for child in self.tree[state]:
                feature_set = list(child.configuration.get_selected_elements() - state.configuration.get_selected_elements())
                if len(feature_set) == 1:
                    feature = feature_set[0]
                    feature_rewards[feature] += self.Q[child]
                    feature_visits[feature] += self.N[child]
        
        # Normalize values to range 0..1
        values = [round(float(feature_rewards[f])/float(feature_visits[f]), 2) if feature_visits[f] > 0 else 0.0 for f in feature_rewards]
        min_value = min(values)
        max_value = max(values)
        normalized_values = {}
        heatmap = {}
        for feature, v in data.items():
            normalized_values[feature] = (v-min_value)/(max_value-min_value)
            heatmap[feature] = assign_color(normalized_values[feature])
            
        with open("MCTS-heatmap.txt", 'w+') as file:
            file.write("Feature, Visits, Acc. Reward, Q-value\n")
            for f in feature_model.get_features():
                file.write(f"{f.name}, {feature_visits[f]}, {feature_rewards[f]}, {feature_rewards[f]/feature_visits[f] if feature_visits[f] > 0 else 0.0}\n")

    def __str__(self) -> str:
        return f"MonteCarlo Tree Search (sc:{str(self.stopping_condition)})"
