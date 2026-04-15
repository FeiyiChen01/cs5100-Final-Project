from __future__ import annotations

from typing import List, Optional

from game_state import GameState, Move, Piece, Position
from game_state import in_black_palace, in_bounds, in_red_palace


def in_palace(side: str, pos: Position) -> bool:
  """Return True if pos is inside the given side's palace."""
  if side == "black":
    return in_black_palace(pos)
  return in_red_palace(pos)


def target_has_friendly_piece(state: GameState, side: str,
    pos: Position) -> bool:
  """Return True if the target square contains a friendly piece."""
  piece = state.piece_at(pos)
  return piece is not None and piece.side == side


def get_between_positions(start: Position, end: Position) -> List[Position]:
  """
  Return all positions strictly between start and end.
  Only valid when start and end are on the same row or same column.
  """
  x1, y1 = start
  x2, y2 = end
  result: List[Position] = []

  if x1 == x2:
    step = 1 if y2 > y1 else -1
    for y in range(y1 + step, y2, step):
      result.append((x1, y))
  elif y1 == y2:
    step = 1 if x2 > x1 else -1
    for x in range(x1 + step, x2, step):
      result.append((x, y1))

  return result


def count_pieces_between(state: GameState, start: Position,
    end: Position) -> int:
  """Count how many pieces lie strictly between start and end."""
  return sum(1 for pos in get_between_positions(start, end) if
             state.piece_at(pos) is not None)


def generals_facing(state: GameState) -> bool:
  """
  Return True if black general and red king are on the same file
  with no piece between them.
  """
  black_general = state.find_piece("black", "K")
  red_king = state.find_piece("red", "K")

  if black_general is None or red_king is None:
    return False

  bx, _ = black_general
  rx, _ = red_king
  if bx != rx:
    return False

  return count_pieces_between(state, black_general, red_king) == 0


def generate_general_moves(state: GameState, pos: Position, piece: Piece) -> \
List[Move]:
  """General and king stay inside palace, move one step orthogonally"""
  moves: List[Move] = []
  x, y = pos

  for dx, dy in [(0, 1), (0, -1), (-1, 0), (1, 0)]:
    target = (x + dx, y + dy)
    if not in_bounds(target):
      continue
    if not in_palace(piece.side, target):
      continue
    if target_has_friendly_piece(state, piece.side, target):
      continue
    moves.append((pos, target))

  return moves


def generate_advisor_moves(state: GameState, pos: Position, piece: Piece) -> \
List[Move]:
  """Advisor stay inside palace, move one step diagonally"""
  moves: List[Move] = []
  x, y = pos

  for dx, dy in [(-1, 1), (1, 1), (-1, -1), (1, -1)]:
    target = (x + dx, y + dy)
    if not in_bounds(target):
      continue
    if not in_palace(piece.side, target):
      continue
    if target_has_friendly_piece(state, piece.side, target):
      continue
    moves.append((pos, target))

  return moves


def generate_black_soldier_moves(state: GameState, pos: Position, piece: Piece) -> \
List[Move]:
  """Soldier one step up, left, right, cannot move backward"""
  moves: List[Move] = []
  x, y = pos

  for dx, dy in [(0, 1), (-1, 0), (1, 0)]:
    target = (x + dx, y + dy)
    if not in_bounds(target):
      continue
    if target_has_friendly_piece(state, piece.side, target):
      continue
    moves.append((pos, target))

  return moves


def generate_red_pawn_moves(state: GameState, pos: Position, piece: Piece) -> \
List[Move]:
  """ red pawn would move one step down, left, right."""
  moves: List[Move] = []
  x, y = pos

  for dx, dy in [(0, -1), (-1, 0), (1, 0)]:
    target = (x + dx, y + dy)
    if not in_bounds(target):
      continue
    if target_has_friendly_piece(state, piece.side, target):
      continue
    moves.append((pos, target))

  return moves


def generate_rook_moves(state: GameState, pos: Position, piece: Piece) -> List[
  Move]:
  """ rook move any number of squares orthogonally,
  cannot jump over pieces, can capture the first enemy piece in a direction """
  moves: List[Move] = []
  x, y = pos

  for dx, dy in [(0, 1), (0, -1), (-1, 0), (1, 0)]:
    nx, ny = x + dx, y + dy
    while in_bounds((nx, ny)):
      target = (nx, ny)
      target_piece = state.piece_at(target)

      if target_piece is None:
        moves.append((pos, target))
      else:
        if target_piece.side != piece.side:
          moves.append((pos, target))
        break

      nx += dx
      ny += dy

  return moves


def generate_cannon_moves(state: GameState, pos: Position, piece: Piece) -> \
List[Move]:
  """ Cannon moves any number of squares orthogonally,
  non-capturing move: path must be clear, destination empty,
  capturing move: there must be exactly one piece between start and target """
  moves: List[Move] = []
  x, y = pos

  for dx, dy in [(0, 1), (0, -1), (-1, 0), (1, 0)]:
    nx, ny = x + dx, y + dy
    seen_screen = False

    while in_bounds((nx, ny)):
      target = (nx, ny)
      target_piece = state.piece_at(target)

      if not seen_screen:
        if target_piece is None:
          moves.append((pos, target))
        else:
          seen_screen = True
      else:
        if target_piece is not None:
          if target_piece.side != piece.side:
            moves.append((pos, target))
          break

      nx += dx
      ny += dy

  return moves


def generate_piece_moves(state: GameState, pos: Position) -> List[Move]:
  piece = state.piece_at(pos)
  if piece is None:
    return []

  if piece.kind == "K":
    return generate_general_moves(state, pos, piece)

  if piece.kind == "A":
    return generate_advisor_moves(state, pos, piece)

  if piece.kind == "P":
    if piece.side == "black":
      return generate_black_soldier_moves(state, pos, piece)
    return generate_red_pawn_moves(state, pos, piece)

  if piece.kind == "R":
    return generate_rook_moves(state, pos, piece)

  if piece.kind == "C":
    return generate_cannon_moves(state, pos, piece)

  return []


def square_attacked_by_piece(state: GameState, attacker_pos: Position,
    target: Position) -> bool:
  """Return True if the piece at attacker_pos attacks target."""
  piece = state.piece_at(attacker_pos)
  if piece is None:
    return False

  x1, y1 = attacker_pos
  x2, y2 = target

  if piece.kind == "K":
    # General and King attack one step orthogonally
    return abs(x1 - x2) + abs(y1 - y2) == 1

  if piece.kind == "A":
    # Advisor/Guard attack one step diagonally
    return abs(x1 - x2) == 1 and abs(y1 - y2) == 1

  if piece.kind == "P":
    if piece.side == "black":
      return target in {(x1, y1 + 1), (x1 - 1, y1), (x1 + 1, y1)}
    return target in {(x1, y1 - 1), (x1 - 1, y1), (x1 + 1, y1)}

  if piece.kind == "R":
    if x1 != x2 and y1 != y2:
      return False
    return count_pieces_between(state, attacker_pos, target) == 0

  if piece.kind == "C":
    if x1 != x2 and y1 != y2:
      return False
    return count_pieces_between(state, attacker_pos, target) == 1

  return False


def is_in_check(state: GameState, side: str) -> bool:
  """Return True if side's general is under attack."""
  general_pos = state.find_piece(side, "K")
  if general_pos is None:
    return True

  if generals_facing(state):
    return True

  opponent = "red" if side == "black" else "black"
  for pos, piece in state.all_pieces():
    if piece.side != opponent:
      continue
    if square_attacked_by_piece(state, pos, general_pos):
      return True

  return False


def is_legal_move(state: GameState, move: Move) -> bool:
  """Return True if move is legal in the current state."""
  source, _ = move
  piece = state.piece_at(source)

  if piece is None:
    return False

  if piece.side != state.turn:
    return False

  pseudo_legal = generate_piece_moves(state, source)
  if move not in pseudo_legal:
    return False

  next_state = state.move_piece(move)

  if generals_facing(next_state):
    return False

  if is_in_check(next_state, piece.side):
    return False

  return True


def generate_legal_moves(state: GameState, side: str) -> List[Move]:
  """Generate all legal moves for the given side."""
  legal_moves: List[Move] = []

  for pos, piece in state.all_pieces():
    if piece.side != side:
      continue

    for move in generate_piece_moves(state, pos):
      next_state = state.move_piece(move)
      if generals_facing(next_state):
        continue
      if is_in_check(next_state, side):
        continue
      legal_moves.append(move)

  return legal_moves


def has_any_legal_move(state: GameState, side: str) -> bool:
  """Return True if the given side has at least one legal move."""
  return len(generate_legal_moves(state, side)) > 0


def winner(state: GameState) -> Optional[str]:
  black_general = state.find_piece("black", "K")
  red_king = state.find_piece("red", "K")

  if black_general is None:
    return "red"
  if red_king is None:
    return "black"

  side = state.turn
  legal_moves = generate_legal_moves(state, side)

  if legal_moves:
    return None

  if is_in_check(state, side):
    return "red" if side == "black" else "black"

  return "draw"
