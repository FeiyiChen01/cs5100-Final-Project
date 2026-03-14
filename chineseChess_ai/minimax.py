from __future__ import annotations

from math import inf
from typing import Optional, Tuple

from evaluation import evaluate
from game_state import GameState, Move
from move_generator import generate_legal_moves, winner


def minimax(
    state: GameState,
    depth: int,
    alpha: int,
    beta: int,
) -> Tuple[int, Optional[Move]]:
  result = winner(state)
  if depth == 0 or result is not None:
    return evaluate(state), None

  side = state.turn
  legal_moves = generate_legal_moves(state, side)

  if not legal_moves:
    return evaluate(state), None

  best_move: Optional[Move] = None

  if side == "red":
    best_score = -inf
    for move in legal_moves:
      child = state.move_piece(move)
      score, _ = minimax(child, depth - 1, alpha, beta)

      if score > best_score:
        best_score = score
        best_move = move

      alpha = max(alpha, int(best_score))
      if beta <= alpha:
        break

    return int(best_score), best_move

  best_score = inf
  for move in legal_moves:
    child = state.move_piece(move)
    score, _ = minimax(child, depth - 1, alpha, beta)

    if score < best_score:
      best_score = score
      best_move = move

    beta = min(beta, int(best_score))
    if beta <= alpha:
      break

  return int(best_score), best_move
