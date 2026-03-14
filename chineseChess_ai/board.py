from __future__ import annotations
from game_state import GameState


def display_board(state: GameState) -> None:
  ###Print the board in a simple command-line format.
  print("    0    1    2    3    4    5    6    7    8")
  print("  +" + "-----+" * 9)

  for r in range(10):
    row_str = f"{r} |"
    for c in range(9):
      piece = state.board[r][c]
      cell = piece.symbol() if piece else "  "
      row_str += f"{cell:^5}|"
    print(row_str)
    print("  +" + "-----+" * 9)

  print(f"Turn: {state.turn}")
  print()
