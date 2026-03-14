from __future__ import annotations
from game_state import GameState
from move_generator import generate_legal_moves, is_in_check, manhattan, winner


def evaluate(state: GameState) -> int:
  result = winner(state)
  if result == "red":
    return 100000
  if result == "black":
    return -100000
  if result == "draw":
    return 0

  score = 0

  black_king = state.find_piece("black", "K")
  red_king = state.find_piece("red", "K")
  red_rook = state.find_piece("red", "R")
  red_pawn = state.find_piece("red", "P")

  # Material-like base values
  if red_rook is not None:
    score += 500
  if red_pawn is not None:
    score += 120

  # Restrict black king mobility
  black_state = GameState(state.board, "black")
  black_moves = len(generate_legal_moves(black_state, "black"))
  score -= 15 * black_moves

  # Bonus if black king is in check
  if is_in_check(black_state, "black"):
    score += 80

  # Encourage rook pressure
  if red_rook is not None and black_king is not None:
    rr, rc = red_rook
    br, bc = black_king
    if rr == br or rc == bc:
      score += 30

  # Encourage pawn to approach black king
  if red_pawn is not None and black_king is not None:
    score += 20 - 2 * manhattan(red_pawn, black_king)

  # Encourage red king support
  if red_king is not None and black_king is not None:
    score += 10 - manhattan(red_king, black_king)

  return score
