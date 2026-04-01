from __future__ import annotations

from math import inf
from typing import Optional, Tuple

from evaluation import evaluate
from game_state import GameState, Move
from move_generator import generate_legal_moves, winner


def move_ordering_score(state: GameState, move: Move) -> int:
    score = 0

    from_row, from_col = move[0]
    to_row, to_col = move[1]

    moving_piece = state.get_piece(from_row, from_col)
    target_piece = state.get_piece(to_row, to_col)

    if target_piece is not None:
        score += 1000

    next_state = state.move_piece(move)
    score += evaluate(next_state)

    # Small bonus for advancing the pawn
    if moving_piece is not None:
        side, piece_type = moving_piece
        if side == "red" and piece_type == "P":
            score += (9 - to_row) * 5
        elif side == "black" and piece_type == "P":
            score += to_row * 5

    return score


def order_moves(state: GameState, legal_moves: list[Move]) -> list[Move]:
    reverse = state.turn == "red"
    return sorted(
        legal_moves,
        key=lambda move: move_ordering_score(state, move),
        reverse=reverse
    )


def minimax(
    state: GameState,
    depth: int,
    alpha: int,
    beta: int,
) -> Tuple[int, Optional[Move]]:
    result = winner(state)
    if depth == 0 or result is not None:
        return evaluate(state), None

    side = state.turn
    legal_moves = generate_legal_moves(state, side)

    if not legal_moves:
        return evaluate(state), None

    legal_moves = order_moves(state, legal_moves)

    best_move: Optional[Move] = None

    if side == "red":
        best_score = -inf

        for move in legal_moves:
            child = state.move_piece(move)
            score, _ = minimax(child, depth - 1, alpha, beta)

            if score > best_score:
                best_score = score
                best_move = move

            alpha = max(alpha, int(best_score))
            if beta <= alpha:
                break

        return int(best_score), best_move

    best_score = inf

    for move in legal_moves:
        child = state.move_piece(move)
        score, _ = minimax(child, depth - 1, alpha, beta)

        if score < best_score:
            best_score = score
            best_move = move

        beta = min(beta, int(best_score))
        if beta <= alpha:
            break

    return int(best_score), best_move