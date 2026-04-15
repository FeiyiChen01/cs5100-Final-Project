from __future__ import annotations

from game_state import GameState
from move_generator import generate_legal_moves, is_in_check, winner

WIN_SCORE = 1_000_000
LOSS_SCORE = -1_000_000
DRAW_SCORE = 0

PIECE_VALUES = {
  "K": 0,  # General/King
  "A": 40,  # Advisor/Guard
  "P": 180,  # Soldier/Pawn
  "C": 300,  # Catapult/Cannon
  "R": 500,  # Chariot/Rook
}


def manhattan(a: tuple[int, int], b: tuple[int, int]) -> int:
  """Return Manhattan distance between two positions."""
  return abs(a[0] - b[0]) + abs(a[1] - b[1])


def evaluate(state: GameState) -> int:
  """
  Return a heuristic score from Red's perspective.
  Larger score, better for red.
  Smaller score, better for black.
  """
  result = winner(state)
  if result == "red":
    return WIN_SCORE
  if result == "black":
    return LOSS_SCORE
  if result == "draw":
    return DRAW_SCORE

  score = 0

  black_king = state.find_piece("black", "K")
  red_king = state.find_piece("red", "K")

  # Material balance
  for pos, piece in state.all_pieces():
    value = PIECE_VALUES[piece.kind]
    if piece.side == "red":
      score += value
    else:
      score -= value

  # Mobility
  red_moves = generate_legal_moves(state, "red")
  black_moves = generate_legal_moves(state, "black")
  score += 10 * (len(red_moves) - len(black_moves))

  # Check status
  if is_in_check(state, "black"):
    score += 220
  if is_in_check(state, "red"):
    score -= 320

  # Pressure on the black king
  if black_king is not None:
    for pos, piece in state.all_pieces():
      if piece.side != "red":
        continue

      distance = manhattan(pos, black_king)

      if piece.kind == "R":
        # Rook pressure matters a lot
        score += max(0, 16 - 2 * distance)

        # Same file or row pressure
        if pos[0] == black_king[0]:
          score += 40
        if pos[1] == black_king[1]:
          score += 40

      elif piece.kind == "C":
        score += max(0, 12 - distance)

        if pos[0] == black_king[0]:
          score += 20
        if pos[1] == black_king[1]:
          score += 20

      elif piece.kind == "K":
        score += max(0, 8 - distance)

  if red_king is not None:
    for pos, piece in state.all_pieces():
      if piece.side == "black" and piece.kind == "P":
        distance = manhattan(pos, red_king)

        score -= max(0, 140 - 25 * distance)

        if pos == (4, 9):
          score -= 400
        elif pos == (4, 8):
          score -= 220
        elif pos == (4, 10):
          score -= 600

  if black_king is not None:
    black_king_moves = 0
    for move in black_moves:
      source, _ = move
      piece = state.piece_at(source)
      if piece is not None and piece.side == "black" and piece.kind == "K":
        black_king_moves += 1
    score += 35 * (4 - black_king_moves)

  if red_king is not None:
    red_king_moves = 0
    for move in red_moves:
      source, _ = move
      piece = state.piece_at(source)
      if piece is not None and piece.side == "red" and piece.kind == "K":
        red_king_moves += 1
    score -= 45 * (4 - red_king_moves)

  # Reward states where red attacks and black is cramped
  if len(black_moves) <= 2:
    score += 120
  if len(red_moves) <= 2:
    score -= 120

  # preference for faster wins or slower losses
  score -= 2 * state.full_turn_count

  return score
