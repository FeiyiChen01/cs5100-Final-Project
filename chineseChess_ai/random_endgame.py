import random
from game_state import GameState, Piece


def random_endgame_state() -> GameState:
    while True:
        grid = [[None for _ in range(9)] for _ in range(10)]

        positions = random.sample([(r, c) for r in range(10) for c in range(9)], 4)
        bk, rk, rr, rp = positions

        grid[bk[0]][bk[1]] = Piece("black", "K")
        grid[rk[0]][rk[1]] = Piece("red", "K")
        grid[rr[0]][rr[1]] = Piece("red", "R")
        grid[rp[0]][rp[1]] = Piece("red", "P")

        state = GameState(tuple(tuple(row) for row in grid), "red")

        return state