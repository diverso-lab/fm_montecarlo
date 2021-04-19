from montecarlo4fms.models import State


class MCTSStats():
    """Step-wise stats"""

    ROUND_DECIMALS = 2

    STEP_STR = 'Step'
    DECISIONS_STR = 'Decisions'
    SIMULATIONS_STR = 'Simulations'
    EVALUATIONS_STR = 'Evaluations'
    POSITIVE_EVALUATIONS_STR = 'Positive Evaluations'
    TREESIZE_STR = "Tree Size"
    TIME_STR = 'Time (s)'
    CHOICE_STR = 'Choice'

    HEADER = [STEP_STR, DECISIONS_STR, SIMULATIONS_STR, EVALUATIONS_STR, POSITIVE_EVALUATIONS_STR, TREESIZE_STR, TIME_STR, CHOICE_STR]

    def __init__(self):
        self.stats = {}

    def add_step(self, step: int, mcts_tree_search: dict, state: State, result_state: State, simulations: int, evaluations: int, positive_evaluations: int, time: float):
        self.stats[step] = {}
        self.stats[step][MCTSStats.STEP_STR] = step
        if state in mcts_tree_search:
            decisions = len(mcts_tree_search[state]) 
        else:
            decisions = 0
        self.stats[step][MCTSStats.DECISIONS_STR] = decisions
        self.stats[step][MCTSStats.SIMULATIONS_STR] = simulations
        self.stats[step][MCTSStats.EVALUATIONS_STR] = evaluations
        self.stats[step][MCTSStats.POSITIVE_EVALUATIONS_STR] = positive_evaluations
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
