from __future__ import annotations

from typing import List

from game_state import GameState, Piece

CELL = 4
TOP_BORDER = "    " + " ".join(f"{x:^{CELL}}" for x in range(1, 10))


def piece_label(piece: Piece | None) -> str:
  return piece.short_name if piece is not None else "·"


def _node_text(state: GameState, x: int, y: int) -> str:
  label = piece_label(state.piece_at((x, y)))
  return f"{label:^{CELL}}"


def _connector() -> str:
  """Return the horizontal connector between point x and x+1 on a printed row."""
  return "─"


def _row_line(state: GameState, y: int) -> str:
  parts: List[str] = [f"{y:>2}  "]

  for x in range(1, 10):
    parts.append(_node_text(state, x, y))
    if x < 9:
      parts.append(_connector())

  return "".join(parts)


def _vertical_line(y: int) -> str:
  """Return the vertical connector row between two printed rows."""
  if y == 5:
    return ""

  cells: List[str] = ["    "]
  for x in range(1, 10):
    cells.append(f"{'│':^{CELL}}")
    if x < 9:
      cells.append(" ")

  return "".join(cells)


def render_board(state: GameState) -> str:
  """Render the board using the same coordinate orientation as the game state."""
  board_width = 9 * CELL + 8

  lines: List[str] = []
  lines.append(TOP_BORDER)
  lines.append("   " + "─" * board_width)

  for y in range(1, 11):
    lines.append(_row_line(state, y))

    if y == 5:
      river_width = board_width
      river_text = "Chu Han River"
      lines.append("    " + f"{river_text:^{river_width}}")
    elif y != 10:
      vertical = _vertical_line(y)
      if vertical:
        lines.append(vertical)

  lines.append("   " + "─" * board_width)
  lines.append(
      "Current turn: " + ("Red" if state.turn == "red" else "Black"))
  lines.append("Input examples: rook(7,1) cannon(5,3) ")
  return "\n".join(lines)


def render_piece_summary(state: GameState) -> str:
  """Show current piece locations."""
  black_parts: List[str] = []
  red_parts: List[str] = []

  for pos, piece in sorted(
      state.all_pieces(),
      key=lambda item: (item[0][1], item[0][0]),
  ):
    label = f"{piece.name}{pos}"
    if piece.side == "black":
      black_parts.append(label)
    else:
      red_parts.append(label)

  return "Black: " + ", ".join(black_parts) + "\n" + "Red: " + ", ".join(
      red_parts)
