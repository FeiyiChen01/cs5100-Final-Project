from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional, Tuple

Position = Tuple[int, int]  # (row, col)
Move = Tuple[Position, Position]


@dataclass(frozen=True)
class Piece:
  side: str  # red or black
  kind: str  # K (king), R (rook), P (pawn)

  def symbol(self) -> str:
    ###Return a short display symbol for the piece.
    mapping = {
      ("red", "K"): "RK",
      ("red", "R"): "RR",
      ("red", "P"): "RP",
      ("black", "K"): "BK",
    }
    return mapping[(self.side, self.kind)]


@dataclass(frozen=True)
class GameState:
  ### Pieces: Red: King, Rook, Pawn Black: King

  board: Tuple[Tuple[Optional[Piece], ...], ...]
  turn: str  # "red" or "black"

  @staticmethod
  def initial() -> "GameState":
    ### Create a default starting position.

    grid = [[None for _ in range(9)] for _ in range(10)]

    # Black king
    grid[1][4] = Piece("black", "K")

    # Red pieces
    grid[9][4] = Piece("red", "K")
    grid[7][0] = Piece("red", "R")
    grid[6][4] = Piece("red", "P")

    return GameState(
        board=tuple(tuple(row) for row in grid),
        turn="red",
    )

  def piece_at(self, pos: Position) -> Optional[Piece]:
    ###Return the piece at the given board position.
    row, col = pos
    return self.board[row][col]

  def find_piece(self, side: str, kind: str) -> Optional[Position]:
    ###Find and return the position of a specific piece.
    for r in range(10):
      for c in range(9):
        piece = self.board[r][c]
        if piece is not None and piece.side == side and piece.kind == kind:
          return (r, c)
    return None

  def all_pieces(self, side: str) -> List[Tuple[Position, Piece]]:
    ###Return all pieces for the given side.
    result: List[Tuple[Position, Piece]] = []
    for r in range(10):
      for c in range(9):
        piece = self.board[r][c]
        if piece is not None and piece.side == side:
          result.append(((r, c), piece))
    return result

  def move_piece(self, move: Move) -> "GameState":
    ###Return a new game state after applying the given move.
    (r1, c1), (r2, c2) = move
    piece = self.board[r1][c1]
    if piece is None:
      raise ValueError("No piece at the source square.")

    new_grid = [list(row) for row in self.board]
    new_grid[r2][c2] = piece
    new_grid[r1][c1] = None

    next_turn = "black" if self.turn == "red" else "red"
    return GameState(
        board=tuple(tuple(row) for row in new_grid),
        turn=next_turn,
    )
