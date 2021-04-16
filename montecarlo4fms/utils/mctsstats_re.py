from montecarlo4fms.models import State


class MCTSStatsRE():
    """Step-wise stats for reverse engineering"""

    ROUND_DECIMALS = 2

    STEP_STR = 'Step'
    DECISIONS_STR = 'Decisions'
    SIMULATIONS_STR = 'Simulations'
    EVALUATIONS_STR = 'Evaluations'
    POSITIVE_EVALUATIONS_STR = 'Positive Evaluations'
    TREESIZE_STR = "Tree Size"
    TIME_STR = 'Time (s)'
    CHOICE_STR = 'Choice'

    HEADER = [STEP_STR, DECISIONS_STR, SIMULATIONS_STR, EVALUATIONS_STR, TREESIZE_STR, TIME_STR, CHOICE_STR]

    def __init__(self, filepath: str):
        self.filepath = filepath
        with open(filepath, 'w+') as file:
            file.write("MCTS stats for reverse engineering\n")

    def add_step(self, step: int, mcts_tree_search: dict, mcts_q_values: dict, mcts_visits: dict, state: State, result_state: State, simulations: int, time: float):
        with open(self.filepath, 'a+') as file:
            file.write(f"State: {str(state)}\n")
            if state in mcts_tree_search:
                file.write(f"#Decisions: {len(mcts_tree_search[state])}\n")
                q_values = {}
                for s in mcts_tree_search[state]:
                    if mcts_visits[s] > 0:
                        q_values[s] = float(mcts_q_values[s])/float(mcts_visits[s])
                    else:
                        q_values[s] = 0
                min_value = min(q_values.values())
                max_value = max(q_values.values())
                n = max_value - min_value
                
                sorted_states = {k: v for k, v in sorted(q_values.items(), key=lambda item: item[1])}
                for s in sorted_states:
                    if n > 0:
                        normalized_value = round((q_values[s]-min_value) / n, MCTSStatsRE.ROUND_DECIMALS)
                    else:
                        normalized_value = q_values[s] / q_values[s]
                    file.write(f"//MC values for state: {str(s)} -> {mcts_q_values[s]}/{mcts_visits[s]} = {q_values[s]} -> normalized: {normalized_value}\n")
            else:
                file.write(f"#Decisions: {0}\n")
            file.write(f"Best decision: {str(result_state)}\n")
            file.write(f"Total nodes in the tree search: {len(mcts_tree_search)}\n")
            file.write(f"Simulations: {simulations}\n")
            file.write(f"Execution time: {time}\n")
            file.write(f"==================================================================================================================================")