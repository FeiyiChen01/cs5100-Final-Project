from __future__ import annotations

from math import inf
from typing import Optional, Tuple, List

from evaluation import evaluate
from game_state import GameState, Move
from move_generator import generate_legal_moves, winner


def move_ordering_score(state: GameState, move: Move) -> int:
  score = 0

  from_pos, to_pos = move
  moving_piece = state.piece_at(from_pos)
  target_piece = state.piece_at(to_pos)

  if target_piece is not None:
    score += 1000

  next_state = state.move_piece(move)
  next_score = evaluate(next_state)

  # Red wants larger evaluation, black wants smaller evaluation
  if state.turn == "red":
    score += next_score
  else:
    score -= next_score

  # Small bonus for pawn advancement
  if moving_piece is not None and moving_piece.kind == "P":
    to_row, _ = to_pos
    if moving_piece.side == "red":
      score += (9 - to_row) * 5
    else:
      score += to_row * 5

  return score


def order_moves(state: GameState, legal_moves: List[Move]) -> List[Move]:
  return sorted(
      legal_moves,
      key=lambda move: move_ordering_score(state, move),
      reverse=True,
  )


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

  legal_moves = order_moves(state, legal_moves)

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
