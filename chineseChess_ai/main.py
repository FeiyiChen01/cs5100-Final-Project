from __future__ import annotations

from math import inf

from board import display_board
from game_state import GameState, Move
from minimax import minimax
from move_generator import generate_legal_moves, winner


def parse_move(text: str) -> Move:
  parts = text.strip().split()
  if len(parts) != 4:
    raise ValueError("Move must be entered as: r1 c1 r2 c2")

  r1, c1, r2, c2 = map(int, parts)
  return (r1, c1), (r2, c2)


def move_to_string(move: Move) -> str:
  (r1, c1), (r2, c2) = move
  return f"({r1}, {c1}) -> ({r2}, {c2})"


def play_cli() -> None:
  state = GameState.initial()
  search_depth = 4

  print("Simplified Xiangqi Endgame: Red (AI) vs Black (You)")
  print("You control the Black King.")
  print("Enter moves as: r1 c1 r2 c2")
  print()

  while True:
    display_board(state)

    result = winner(state)
    if result is not None:
      if result == "draw":
        print("Game over: draw.")
      else:
        print(f"Game over: {result} wins.")
      break

    if state.turn == "red":
      score, best_move = minimax(state, search_depth, -inf, inf)
      if best_move is None:
        print("AI has no legal move.")
        break

      print(f"AI chooses: {move_to_string(best_move)} [eval={score}]")
      state = state.move_piece(best_move)
    else:
      legal = generate_legal_moves(state, "black")
      print("Your legal moves:")
      for idx, mv in enumerate(legal):
        print(f"  {idx}: {move_to_string(mv)}")

      user_input = input("Enter your move: ").strip()
      try:
        move = parse_move(user_input)
      except ValueError as error:
        print(f"Invalid input: {error}")
        continue

      if move not in legal:
        print("That move is not legal.")
        continue

      state = state.move_piece(move)


if __name__ == "__main__":
  play_cli()
