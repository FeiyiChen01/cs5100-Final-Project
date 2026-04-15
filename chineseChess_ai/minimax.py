from __future__ import annotations

from math import inf
from typing import Optional, Tuple

from evaluation import evaluate
from game_state import GameState, Move
from move_generator import generate_legal_moves, is_in_check, winner


def move_priority(state: GameState, candidate_move: Move) -> int:
  """
  Return a heuristic priority for move ordering. Larger value means the move should be searched earlier.
  """
  source, target = candidate_move
  moving_piece = state.piece_at(source)
  target_piece = state.piece_at(target)

  priority = 0

  if target_piece is not None:
    capture_bonus = {
      "K": 100000,
      "R": 1200,
      "C": 900,
      "P": 700,
      "A": 400,
    }
    priority += capture_bonus.get(target_piece.kind, 500)

  # black pawn reaching key attacking squares matters a lot.
  if moving_piece is not None and moving_piece.side == "black" and moving_piece.kind == "P":
    if target == (4, 9):
      priority += 1500
    elif target == (4, 10):
      priority += 2000

  # Prefer moves that give check.
  next_state = state.move_piece(candidate_move)
  opponent = "black" if state.turn == "red" else "red"
  if is_in_check(next_state, opponent):
    priority += 1000

  # add a small amount of evaluation-based ordering.
  next_score = evaluate(next_state)
  if state.turn == "red":
    priority += next_score
  else:
    priority -= next_score

  return priority


def order_moves(state: GameState, legal_moves: list[Move]) -> list[Move]:
  return sorted(
      legal_moves,
      key=lambda move: move_priority(state, move),
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

  ordered_moves = order_moves(state, legal_moves)
  best_move: Optional[Move] = None

  if side == "red":
    best_score = -inf

    for candidate_move in ordered_moves:
      child = state.move_piece(candidate_move)
      child_score, _ = minimax(child, depth - 1, alpha, beta)

      if child_score > best_score:
        best_score = child_score
        best_move = candidate_move

      alpha = max(alpha, int(best_score))
      if alpha >= beta:
        break

    return int(best_score), best_move

  best_score = inf

  for candidate_move in ordered_moves:
    child = state.move_piece(candidate_move)
    child_score, _ = minimax(child, depth - 1, alpha, beta)

    if child_score < best_score:
      best_score = child_score
      best_move = candidate_move

    beta = min(beta, int(best_score))
    if alpha >= beta:
      break

  return int(best_score), best_move


def choose_best_move(state: GameState, depth: int = 2) -> Optional[Move]:
  """
  public helper for selecting the best move from the current position.
  """
  legal_moves = generate_legal_moves(state, state.turn)
  if not legal_moves:
    return None

  _, best_move = minimax(state, depth, -inf, inf)
  return best_move
