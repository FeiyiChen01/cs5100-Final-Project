from __future__ import annotations

from game_state import GameState
from move_generator import generate_legal_moves, is_in_check, manhattan, winner


WIN_SCORE = 100000
LOSS_SCORE = -100000
DRAW_SCORE = 0


def evaluate(state: GameState) -> int:
    result = winner(state)
    if result == "red":
        return WIN_SCORE
    if result == "black":
        return LOSS_SCORE
    if result == "draw":
        return DRAW_SCORE

    score = 0

    black_king = state.find_piece("black", "K")
    red_king = state.find_piece("red", "K")
    red_rook = state.find_piece("red", "R")
    red_pawn = state.find_piece("red", "P")

    # Base material values
    if red_rook is not None:
        score += 500
    if red_pawn is not None:
        score += 120

    black_state = GameState(state.board, "black")
    black_moves = generate_legal_moves(black_state, "black")
    score -= 15 * len(black_moves)

    red_state = GameState(state.board, "red")
    red_moves = generate_legal_moves(red_state, "red")
    score += 3 * len(red_moves)

    # Bonus if black king is currently in check
    if is_in_check(black_state, "black"):
        score += 80

    # Rook pressure: rook on same row or column as black king
    if red_rook is not None and black_king is not None:
        rr, rc = red_rook
        br, bc = black_king

        if rr == br or rc == bc:
            score += 40

        # Encourage rook to get closer to black king
        rook_distance = manhattan(red_rook, black_king)
        score += max(0, 14 - rook_distance)

    # Pawn pressure: encourage pawn to approach black king
    if red_pawn is not None and black_king is not None:
        pawn_distance = manhattan(red_pawn, black_king)
        score += max(0, 20 - 2 * pawn_distance)

        # Extra value if pawn has crossed the river
        pr, _ = red_pawn
        if pr <= 4:
            score += 40

    if red_king is not None and black_king is not None:
        king_distance = manhattan(red_king, black_king)
        if 2 <= king_distance <= 5:
            score += 20
        elif king_distance > 5:
            score -= 10

    # Bonus for confining black king toward palace corners or edges
    if black_king is not None:
        br, bc = black_king

        # In this simplified endgame, black king is strongest when mobile.
        # Encourage states where the king is pushed toward corner-like areas.
        if (br, bc) in {(0, 3), (0, 5), (2, 3), (2, 5)}:
            score += 25
        elif bc == 4:
            score -= 10

    return score