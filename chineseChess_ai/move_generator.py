from __future__ import annotations
from typing import List, Optional
from game_state import GameState, Move, Position


def in_bounds(pos: Position) -> bool:
  r, c = pos
  return 0 <= r < 10 and 0 <= c < 9


def in_palace(side: str, pos: Position) -> bool:
  r, c = pos
  if side == "red":
    return 7 <= r <= 9 and 3 <= c <= 5
  return 0 <= r <= 2 and 3 <= c <= 5


def manhattan(a: Position, b: Position) -> int:
  return abs(a[0] - b[0]) + abs(a[1] - b[1])


def generate_king_moves(state: GameState, pos: Position, side: str) -> List[
  Move]:
  moves: List[Move] = []
  r, c = pos

  for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
    nxt = (r + dr, c + dc)
    if in_bounds(nxt) and in_palace(side, nxt):
      target = state.piece_at(nxt)
      if target is None or target.side != side:
        moves.append((pos, nxt))

  return moves


def generate_rook_moves(state: GameState, pos: Position, side: str) -> List[
  Move]:
  moves: List[Move] = []
  r, c = pos

  for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
    nr, nc = r + dr, c + dc
    while in_bounds((nr, nc)):
      target = state.piece_at((nr, nc))
      if target is None:
        moves.append((pos, (nr, nc)))
      else:
        if target.side != side:
          moves.append((pos, (nr, nc)))
        break
      nr += dr
      nc += dc

  return moves


def generate_pawn_moves(state: GameState, pos: Position, side: str) -> List[
  Move]:
  moves: List[Move] = []
  r, c = pos
  candidates: List[Position] = []

  if side == "red":
    # Red moves upward
    candidates.append((r - 1, c))
    # After crossing the river, red pawn can move left or right
    if r <= 4:
      candidates.append((r, c - 1))
      candidates.append((r, c + 1))
  else:
    # Included for completeness
    candidates.append((r + 1, c))
    if r >= 5:
      candidates.append((r, c - 1))
      candidates.append((r, c + 1))

  for nxt in candidates:
    if in_bounds(nxt):
      target = state.piece_at(nxt)
      if target is None or target.side != side:
        moves.append((pos, nxt))

  return moves


def kings_facing(state: GameState) -> bool:
  ###Return True if the two kings face each other directly on the same file with no piece in between.
  red_king = state.find_piece("red", "K")
  black_king = state.find_piece("black", "K")

  if red_king is None or black_king is None:
    return False

  rr, rc = red_king
  br, bc = black_king

  if rc != bc:
    return False

  start = min(rr, br) + 1
  end = max(rr, br)
  for r in range(start, end):
    if state.board[r][rc] is not None:
      return False

  return True


def is_in_check(state: GameState, side: str) -> bool:
  king_pos = state.find_piece(side, "K")
  if king_pos is None:
    return True

  opponent = "black" if side == "red" else "red"

  if kings_facing(state):
    return True

  rook_pos = state.find_piece(opponent, "R")
  if rook_pos is not None:
    kr, kc = king_pos
    rr, rc = rook_pos

    if kr == rr:
      step = 1 if kc > rc else -1
      blocked = False
      for c in range(rc + step, kc, step):
        if state.board[rr][c] is not None:
          blocked = True
          break
      if not blocked:
        return True

    if kc == rc:
      step = 1 if kr > rr else -1
      blocked = False
      for r in range(rr + step, kr, step):
        if state.board[r][rc] is not None:
          blocked = True
          break
      if not blocked:
        return True

  return False


def generate_pseudo_legal_moves(state: GameState, side: str) -> List[Move]:
  moves: List[Move] = []

  for pos, piece in state.all_pieces(side):
    if piece.kind == "K":
      moves.extend(generate_king_moves(state, pos, side))
    elif piece.kind == "R":
      moves.extend(generate_rook_moves(state, pos, side))
    elif piece.kind == "P":
      moves.extend(generate_pawn_moves(state, pos, side))

  return moves


def generate_legal_moves(state: GameState, side: str) -> List[Move]:
  legal_moves: List[Move] = []

  for move in generate_pseudo_legal_moves(state, side):
    next_state = state.move_piece(move)
    if not is_in_check(next_state, side):
      legal_moves.append(move)

  return legal_moves


def winner(state: GameState) -> Optional[str]:
  ###'red' if red wins  'black' if black wins. 'draw' if draw. None if the game is still ongoing
  red_king = state.find_piece("red", "K")
  black_king = state.find_piece("black", "K")

  if black_king is None:
    return "red"
  if red_king is None:
    return "black"

  side = state.turn
  legal = generate_legal_moves(state, side)

  if not legal:
    if is_in_check(state, side):
      return "black" if side == "red" else "red"
    return "draw"

  return None
