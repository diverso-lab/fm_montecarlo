from montecarlo4fms.models import State


class MCTSStatsIts():
    """Iterations stats"""

    ROUND_DECIMALS = 2

    METHOD_STR = 'Method'
    ITERATIONS_STR = 'Iterations'
    STEPS_STR = 'Decisions'
    SIMULATIONS_STR = 'Simulations'
    EVALUATIONS_STR = 'Evaluations'
    POSITIVE_EVALUATIONS_STR = 'PositiveEvaluations'
    PERCENTAGE_POSITIVE_EVALUATIONS_STR = 'Percentage'
    TREESIZE_STR = 'TreeSize'
    TIME_STR = 'Time'

    HEADER = [METHOD_STR, ITERATIONS_STR, STEPS_STR, SIMULATIONS_STR, EVALUATIONS_STR, POSITIVE_EVALUATIONS_STR, PERCENTAGE_POSITIVE_EVALUATIONS_STR, TREESIZE_STR, TIME_STR]

    def __init__(self):
        self.stats = {}

    def add_step(self, method: str, steps: int, mcts_tree_search: dict, simulations: int, evaluations: int, positive_evaluations: int, time: float):
        self.stats[simulations] = {}
        self.stats[simulations][MCTSStatsIts.METHOD_STR] = f'"{method}"'
        self.stats[simulations][MCTSStatsIts.STEPS_STR] = steps
        self.stats[simulations][MCTSStatsIts.ITERATIONS_STR] = simulations
        self.stats[simulations][MCTSStatsIts.SIMULATIONS_STR] = simulations
        self.stats[simulations][MCTSStatsIts.EVALUATIONS_STR] = evaluations
        self.stats[simulations][MCTSStatsIts.POSITIVE_EVALUATIONS_STR] = positive_evaluations
        self.stats[simulations][MCTSStatsIts.PERCENTAGE_POSITIVE_EVALUATIONS_STR] = float(positive_evaluations) / float(evaluations)
        self.stats[simulations][MCTSStatsIts.TREESIZE_STR] = 0 if mcts_tree_search is None else len(mcts_tree_search)
        self.stats[simulations][MCTSStatsIts.TIME_STR] = time
        
    def serialize(self, filepath: str): 
        with open(filepath, 'w+') as file:
            header = ", ".join(MCTSStatsIts.HEADER)
            file.write(f"{header}\n")
            for its in sorted(self.stats.keys()):
                line = ", ".join(str(self.stats[its][h]) for h in MCTSStatsIts.HEADER)
                file.write(f"{line}\n")
