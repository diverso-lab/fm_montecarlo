from montecarlo4fms.models import State


class MCTSStats():
    ROUND_DECIMALS = 2

    STEP_STR = 'Step'
    DECISIONS_STR = 'Decisions'
    SIMULATIONS_STR = 'Simulations'
    EVALUATIONS_STR = 'Evaluations'
    TREESIZE_STR = "Tree Size"
    TIME_STR = 'Time (s)'
    CHOICE_STR = 'Choice'

    HEADER = [STEP_STR, DECISIONS_STR, SIMULATIONS_STR, EVALUATIONS_STR, TREESIZE_STR, TIME_STR, CHOICE_STR]

    def __init__(self):
        self.stats = {}

    def add_step(self, step: int, mcts_tree_search: dict, state: State, result_state: State, simulations: int, evaluations: int, time: float):
        self.stats[step] = {}
        self.stats[step][MCTSStats.STEP_STR] = step
        self.stats[step][MCTSStats.DECISIONS_STR] = len(mcts_tree_search[state])
        self.stats[step][MCTSStats.SIMULATIONS_STR] = simulations
        self.stats[step][MCTSStats.EVALUATIONS_STR] = evaluations
        self.stats[step][MCTSStats.TREESIZE_STR] = len(mcts_tree_search)
        self.stats[step][MCTSStats.TIME_STR] = time
        self.stats[step][MCTSStats.CHOICE_STR] = list(result_state.configuration.get_selected_elements() - state.configuration.get_selected_elements())[0].name
        
    def serialize(self, filepath: str): 
        with open(filepath, 'w+') as file:
            header = ", ".join(MCTSStats.HEADER)
            file.write(f"{header}\n")
            for step in sorted(self.stats.keys()):
                line = ", ".join(str(self.stats[step][h]) for h in MCTSStats.HEADER)
                file.write(f"{line}\n")
