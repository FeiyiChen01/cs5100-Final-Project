import random

from game_state import GameState, Piece
from move_generator import kings_facing


def random_endgame_state() -> GameState:
  while True:
    grid = [[None for _ in range(9)] for _ in range(10)]

    # Kings must stay inside their palaces
    black_king = (random.randint(0, 2), random.randint(3, 5))
    red_king = (random.randint(7, 9), random.randint(3, 5))

    # Rook and pawn can be anywhere on the board
    red_rook = (random.randint(0, 9), random.randint(0, 8))
    red_pawn = (random.randint(0, 9), random.randint(0, 8))

    positions = {black_king, red_king, red_rook, red_pawn}
    if len(positions) < 4:
      continue

    bk_r, bk_c = black_king
    rk_r, rk_c = red_king
    rr_r, rr_c = red_rook
    rp_r, rp_c = red_pawn

    grid[bk_r][bk_c] = Piece("black", "K")
    grid[rk_r][rk_c] = Piece("red", "K")
    grid[rr_r][rr_c] = Piece("red", "R")
    grid[rp_r][rp_c] = Piece("red", "P")

    state = GameState(
        tuple(tuple(row) for row in grid),
        "red",
    )

    # Avoid illegal king-facing positions
    if kings_facing(state):
      continue

    return state
