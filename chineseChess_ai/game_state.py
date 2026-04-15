from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, Optional, Tuple

Position = Tuple[int, int]
Move = Tuple[Position, Position]

BLACK_PALACE_X = range(4, 7)
BLACK_PALACE_Y = range(1, 4)
RED_PALACE_X = range(4, 7)
RED_PALACE_Y = range(8, 11)

PIECE_NAMES = {
  ("black", "K"): "General",
  ("black", "A"): "Advisor",
  ("black", "P"): "Soldier",
  ("red", "K"): "King",
  ("red", "C"): "Cannon",
  ("red", "R"): "Rook",
}

PIECE_SHORT_NAMES = {
  ("black", "K"): "GE",
  ("black", "A"): "AD",
  ("black", "P"): "SO",
  ("red", "K"): "KI",
  ("red", "C"): "CN",
  ("red", "R"): "RO",
}


@dataclass(frozen=True)
class Piece:
  side: str  # red or black
  kind: str  # K, A, P, C, R

  @property
  def name(self) -> str:
    return PIECE_NAMES[(self.side, self.kind)]

  @property
  def short_name(self) -> str:
    return PIECE_SHORT_NAMES[(self.side, self.kind)]


@dataclass(frozen=True)
class GameState:
  pieces: Dict[Position, Piece]
  turn: str
  full_turn_count: int = 1

  def piece_at(self, pos: Position) -> Optional[Piece]:
    return self.pieces.get(pos)

  def all_pieces(self) -> Iterable[Tuple[Position, Piece]]:
    return self.pieces.items()

  def pieces_of_side(self, side: str) -> Dict[Position, Piece]:
    return {pos: piece for pos, piece in self.pieces.items() if
            piece.side == side}

  def find_piece(self, side: str, kind: str) -> Optional[Position]:
    for pos, piece in self.pieces.items():
      if piece.side == side and piece.kind == kind:
        return pos
    return None

  def positions_of_kind(self, side: str, kind: str) -> Tuple[Position, ...]:
    return tuple(
        pos for pos, piece in self.pieces.items() if
        piece.side == side and piece.kind == kind
    )

  def move_piece(self, move: Move) -> "GameState":
    """Return a new state after applying a legal move."""
    source, target = move
    piece = self.piece_at(source)
    if piece is None:
      raise ValueError(f"There is no piece at {source}.")

    new_pieces = dict(self.pieces)
    new_pieces.pop(source)
    new_pieces[target] = piece

    next_turn = "black" if self.turn == "red" else "red"
    next_full_turn = self.full_turn_count + (1 if next_turn == "red" else 0)
    return GameState(new_pieces, next_turn, next_full_turn)


def in_bounds(pos: Position) -> bool:
  x, y = pos
  return 1 <= x <= 9 and 1 <= y <= 10


def in_black_palace(pos: Position) -> bool:
  x, y = pos
  return x in BLACK_PALACE_X and y in BLACK_PALACE_Y


def in_red_palace(pos: Position) -> bool:
  x, y = pos
  return x in RED_PALACE_X and y in RED_PALACE_Y
