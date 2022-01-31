import copy 
import random 
from typing import Optional

from montecarlo_framework.models.problem import State, Action, Problem
from montecarlo_framework.models.search_space import Solution


class ButtonManiaState(State):

    def __init__(self, n: int, k: int, values: list[list[int]], max_taps: int = -1, n_taps: int = 0):
        assert len(values) == len(values[0]) == n
        self.values = values
        self.N = n 
        self.K = k
        self.n_taps = n_taps
        self.addition = sum([e for sublist in self.values for e in sublist])
        self.max_taps = self.addition if max_taps < 0 else max_taps

    def actions(self) -> list[Action]:
        return [PushButton((x,y)) for x in range(self.N) for y in range(self.N)]

    def successors(self, action: Action) -> list[State]:
        new_values = copy.deepcopy(self.values)
        i, j = action.pos
        for row in range(-1, 2, 1):
            for col in range(-1, 2, 1):
                if row == 0 or col == 0:
                    x = i + row 
                    y = j + col
                    if x >= 0 and x < self.N and y >= 0 and y < self.N:
                        new_values[x][y] = self.K if new_values[x][y] == 0 else new_values[x][y]-1
        new_state = ButtonManiaState(self.N, self.K, new_values, self.max_taps, self.n_taps + 1)
        return [new_state]

    def random_successor(self) -> tuple[State, Action]:
        random_action = random.choice(self.actions())
        random_successor = random.choice(self.successors(random_action))
        return (random_successor, random_action)

    def is_terminal(self) -> bool:
        return self.addition == 0 or self.n_taps > self.max_taps * 2

    def __hash__(self) -> int:
        return hash(tuple([e for sublist in self.values for e in sublist]))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ButtonManiaState):
            return False 
        return self.values == other.values 

    def __str__(self) -> str:
        return str(self.values)

    def heuristic(self) -> float:
        return self.addition / 4 - 1

    def reward(self) -> float:
        if self.addition == 0:
            return 1
        else:
            return -1

class PushButton(Action):

    @staticmethod
    def get_name() -> str:
        return 'Push button.'

    def __init__(self, pos: tuple[int, int]):
        self.pos = pos

    def cost(self, state1: 'State', state2: 'State') -> float:
        return 1.0

    def is_applicable(self, state: 'State') -> bool:
        x, y = self.pos
        return x >= 0 and x < state.N and y >= 0 and y < state.N

    def __str__(self) -> str:
        return str(self.pos)


class ButtonManiaProblem(Problem):

    @staticmethod
    def get_name() -> str:
        return 'Buttom Mania'

    def __init__(self, initial_state: State):
        self.initial_state = initial_state

    def get_initial_state(self) -> 'State':
        return self.initial_state
