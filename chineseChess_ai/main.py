from __future__ import annotations

import re
from math import inf
from typing import List, Optional, Tuple

from board import render_board, render_piece_summary
from evaluation import evaluate
from game_state import GameState, Move, Position
from move_generator import generate_legal_moves, is_in_check, winner
from setup_position import initial_state

try:
  from minimax import choose_best_move

  HAS_CHOOSE_BEST_MOVE = True
except ImportError:
  HAS_CHOOSE_BEST_MOVE = False
  choose_best_move = None

INPUT_PATTERN = re.compile(
    r"^\s*(King|Cannon|Rook)\s*\(\s*(\d+)\s*,\s*(\d+)\s*\)\s*$",
    re.IGNORECASE,
)


def parse_player_input(text: str) -> Tuple[str, Position]:
  match = INPUT_PATTERN.fullmatch(text)
  if match is None:
    raise ValueError(
        "Invalid input format. Use King(4,10), Cannon(5,9), or Rook(6,10)."
    )

  piece_name = match.group(1).capitalize()
  x = int(match.group(2))
  y = int(match.group(3))

  if not (1 <= x <= 9 and 1 <= y <= 10):
    raise ValueError(
        "Coordinates out of range. x must be 1-9 and y must be 1-10.")

  return piece_name, (x, y)


def piece_name_to_kind(piece_name: str) -> str:
  mapping = {
      "King": "K",
      "Cannon": "C",
      "Rook": "R",
      "General": "K",
      "Advisor": "A",
      "Soldier": "P",
  }
  if piece_name not in mapping:
    raise ValueError(f"Unsupported piece name: {piece_name}")
  return mapping[piece_name]


def piece_display_name(piece) -> str:
  if piece is None:
    return "?"
  mapping = {
      ("black", "K"): "General",
      ("black", "A"): "Advisor",
      ("black", "P"): "Soldier",
      ("red", "K"): "King",
      ("red", "C"): "Cannon",
      ("red", "R"): "Rook",
  }
  return mapping.get((piece.side, piece.kind), piece.kind)


def move_to_text(state: GameState, move: Move) -> str:
  """Return move string."""
  source, target = move
  piece = state.piece_at(source)
  piece_name = piece_display_name(piece)
  return f"{piece_name}{source} to {target}"


def legal_moves_for_named_red_piece(state: GameState,
    piece_name: str) -> List[Move]:
  """Return all legal moves for the current red piece name."""
  if state.turn != "red":
    return []

  kind = piece_name_to_kind(piece_name)
  legal = generate_legal_moves(state, "red")
  result: List[Move] = []

  for candidate_move in legal:
    source, _ = candidate_move
    piece = state.piece_at(source)
    if piece is None:
      continue
    if piece.side != "red":
      continue
    if piece.kind == kind:
      result.append(candidate_move)

  return result


def find_player_move_by_target(
    state: GameState,
    piece_name: str,
    target: Position,
) -> Move:
  candidate_moves = legal_moves_for_named_red_piece(state, piece_name)
  matching = [
      candidate_move for candidate_move in candidate_moves
      if candidate_move[1] == target
  ]

  if not matching:
    available_targets = [candidate_move[1] for candidate_move in
                         candidate_moves]
    if available_targets:
      formatted = ", ".join(str(pos) for pos in sorted(available_targets))
      raise ValueError(
          f"{piece_name} cannot move to {target}. Legal targets: {formatted}"
      )
    raise ValueError(f"{piece_name} has no legal moves right now.")

  if len(matching) > 1:
    formatted = "; ".join(move_to_text(state, mv) for mv in matching)
    raise ValueError(
        f"Ambiguous input: multiple {piece_name}s can move to {target}: {formatted}"
    )

  return matching[0]


def describe_position_status(state: GameState) -> str:
  """Return a position status."""
  black_in_check = is_in_check(state, "black")
  red_in_check = is_in_check(state, "red")

  if black_in_check and red_in_check:
    return "Position status: both Black General and Red King are in check."
  if black_in_check:
    return "Position status: Black General is in check."
  if red_in_check:
    return "Position status: Red King is in check."
  return "Position status: neither side is in check."


def pick_black_ai_move(state: GameState, depth: int = 2) -> Optional[Move]:
  """Black move."""
  legal_moves = generate_legal_moves(state, "black")
  if not legal_moves:
    return None

  if HAS_CHOOSE_BEST_MOVE and choose_best_move is not None:
    return choose_best_move(state, depth)

  best_score = inf
  best_move: Optional[Move] = None

  for candidate_move in legal_moves:
    next_state = state.move_piece(candidate_move)
    score = evaluate(next_state)
    if score < best_score:
      best_score = score
      best_move = candidate_move

  return best_move


def print_red_help(state: GameState) -> None:
  """Print player help and current legal targets for red pieces."""
  print("Input format: King(4,10)   Cannon(5,9)   Rook(6,10)")

  red_legal = generate_legal_moves(state, "red")
  if not red_legal:
    return

  grouped: dict[str, List[Position]] = {"King": [], "Cannon": [], "Rook": []}
  for candidate_move in red_legal:
    source, target = candidate_move
    piece = state.piece_at(source)
    if piece is None or piece.side != "red":
      continue
    grouped.setdefault(piece_display_name(piece), []).append(target)

  print("Current legal targets for Red:")
  for name in ["King", "Cannon", "Rook"]:
    targets = sorted(grouped.get(name, []))
    if targets:
      joined = ", ".join(str(pos) for pos in targets)
      print(f"  {name}: {joined}")


def announce_result(result: str) -> None:
  """Print final game result."""
  print()
  if result == "black":
    print("Game over: Black wins.")
    print("Black checkmates the Red King.")
  elif result == "red":
    print("Game over: Red wins.")
    print("Red checkmates the Black General.")
  elif result == "draw":
    print("Game over: Draw.")
    print("The side to move has no legal moves and is not checkmated.")
  else:
    print(f"Game over: {result}")


def print_turn_header(state: GameState) -> None:
  """Print board, summary, and current status."""
  print()
  print(render_board(state))
  print()
  print(render_piece_summary(state))
  print(describe_position_status(state))
  print()


def black_ai_turn(state: GameState) -> GameState:
  """Handle one black AI turn."""
  print_turn_header(state)

  result = winner(state)
  if result is not None:
    announce_result(result)
    return state

  print("Black AI is thinking...")
  ai_move = pick_black_ai_move(state, depth=2)

  if ai_move is None:
    result = winner(state)
    announce_result(result if result is not None else "draw")
    return state

  print(f"Black AI chooses: {move_to_text(state, ai_move)}")
  next_state = state.move_piece(ai_move)

  result = winner(next_state)
  if result is not None:
    print_turn_header(next_state)
    announce_result(result)

  return next_state


def red_player_turn(state: GameState) -> GameState:
  """Handle one red player turn."""
  print_turn_header(state)

  result = winner(state)
  if result is not None:
    announce_result(result)
    return state

  print("Red to move.")
  print_red_help(state)

  while True:
    user_input = input("Enter your move: ").strip()

    if user_input.lower() in {"quit", "exit"}:
      print("You ended the game.")
      return state

    try:
      piece_name, target = parse_player_input(user_input)
      chosen_move = find_player_move_by_target(state, piece_name, target)
    except ValueError as error:
      print(f"Invalid input: {error}")
      continue

    print(f"You chose: {move_to_text(state, chosen_move)}")
    next_state = state.move_piece(chosen_move)

    result = winner(next_state)
    if result is not None:
      print_turn_header(next_state)
      announce_result(result)

    return next_state


def print_intro() -> None:
  """Print game introduction and custom rules."""
  print("Rules:")
  print("1. Black is controlled by the AI. Red is controlled by the player.")
  print("2. Red moves first, then Black.")
  print(
      "3. You enter a piece name and a target coordinate. For example: King(4,10), Cannon(5,9), or Rook(6,10).")
  print(
      "4. The General and King may not face each other directly on the same file without a piece in between.")
  print(
      "5. Red wins by checkmating the Black General. Black wins by checkmating the Red King.")
  print("6. Type quit or exit to stop the game.")
  print("")


def main() -> None:
  """Run the command-line game loop."""
  print_intro()
  state = initial_state()

  while True:
    result = winner(state)
    if result is not None:
      print_turn_header(state)
      announce_result(result)
      break

    if state.turn == "red":
      next_state = red_player_turn(state)
    else:
      next_state = black_ai_turn(state)

    if next_state == state:
      break

    state = next_state


if __name__ == "__main__":
  main()