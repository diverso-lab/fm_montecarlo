
from montecarlo_framework.algorithms import FlatMonteCarlo, AStarSearch
from montecarlo_framework.algorithms.stopping_conditions import IterationsStoppingCondition, NoneStoppingCondition
from montecarlo_framework.algorithms.selection_criterias import MaxChild
from montecarlo_framework.problems.button_mania.button_mania import ButtonManiaState, ButtonManiaProblem

N = 3
K = 3
INITIAL_VALUES2 = [[3, 3, 1, 0, 0, 0],
                 [0, 3, 2, 1, 0, 0],
                 [2, 1, 2, 0, 1, 0],
                 [1, 3, 1, 2, 2, 1],
                 [1, 1, 2, 1, 3, 2],
                 [3, 0, 0, 1, 3, 2]]

INITIAL_VALUES = [[2, 1, 3],
                 [1, 3, 1],
                 [0, 1, 0]]

INITIAL_VALUES3 = [[0, 1, 0],
                 [1, 1, 1],
                 [0, 1, 0]]

def main():
    initial_state = ButtonManiaState(N, K, INITIAL_VALUES)
    print(f'Initial state: {initial_state}')

    # for child in initial_state.successors():
    #     print(f'Children: {child}')

    problem = ButtonManiaProblem(initial_state)

    stopping_condition = NoneStoppingCondition()
    iteration_stopping_condition = IterationsStoppingCondition(iterations=10000)

    selection_criteria = MaxChild()
    alg = FlatMonteCarlo(stopping_condition, selection_criteria, iteration_stopping_condition)
    #alg = AStarSearch()

    solution = alg.run(problem)
    print('Solution:')
    for step, node in enumerate(solution.get_solution_path()):
        state, action = node
        print(f'Step {step}: {str(action)} -> {str(state)}')

if __name__ == '__main__':
    main()