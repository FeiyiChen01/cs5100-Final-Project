from __future__ import annotations

from game_state import GameState, Piece


def initial_state() -> GameState:
  pieces = {
    (4, 1): Piece("black", "K"),  # Black General
    (5, 2): Piece("black", "A"),  # Black Advisor
    (4, 8): Piece("black", "P"),  # Black Soldier
    (4, 10): Piece("red", "K"),  # Red King
    (5, 9): Piece("red", "C"),  # Red Cannon 1
    (5, 10): Piece("red", "C"),  # Red Cannon 2
    (6, 10): Piece("red", "R"),  # Red Rook 1
    (7, 10): Piece("red", "R"),  # Red Rook 2
  }
  return GameState(pieces=pieces, turn="red", full_turn_count=1)
