from __future__ import annotations

import random
from statistics import mean

from evaluation import evaluate
from minimax import choose_best_move
from move_generator import generate_legal_moves, winner
from setup_position import initial_state


def choose_random_move(state):
  legal_moves = generate_legal_moves(state, state.turn)
  if not legal_moves:
    return None
  return random.choice(legal_moves)


def choose_greedy_move(state):
  legal_moves = generate_legal_moves(state, state.turn)
  if not legal_moves:
    return None

  if state.turn == "red":
    return max(legal_moves, key=lambda move: evaluate(state.move_piece(move)))
  else:
    return min(legal_moves, key=lambda move: evaluate(state.move_piece(move)))


def choose_policy_move(state, policy: str):
  if policy == "ai":
    return choose_best_move(state, depth=2)
  if policy == "random":
    return choose_random_move(state)
  if policy == "greedy":
    return choose_greedy_move(state)
  raise ValueError(f"Unknown policy: {policy}")


def play_game(red_policy: str, black_policy: str, max_plies: int = 50):
  state = initial_state()
  plies = 0

  while plies < max_plies:
    result = winner(state)
    if result is not None:
      return result, plies

    if state.turn == "red":
      move = choose_policy_move(state, red_policy)
    else:
      move = choose_policy_move(state, black_policy)

    if move is None:
      result = winner(state)
      return result if result is not None else "draw", plies

    state = state.move_piece(move)
    plies += 1

  return "draw", plies


def run_matchup(red_policy: str, black_policy: str, num_games: int):
  results = []
  for _ in range(num_games):
    results.append(play_game(red_policy, black_policy))

  black_wins = sum(1 for result, _ in results if result == "black")
  red_wins = sum(1 for result, _ in results if result == "red")
  draws = sum(1 for result, _ in results if result == "draw")
  avg_plies = mean(plies for _, plies in results)

  print(f"Red = {red_policy}, Black = {black_policy}, Games = {num_games}")
  print(f"Black wins: {black_wins}")
  print(f"Red wins: {red_wins}")
  print(f"Draws: {draws}")
  print(f"Average plies: {avg_plies:.2f}")
  print()


def main():
  random.seed(5100)

  run_matchup(red_policy="random", black_policy="ai", num_games=50)
  run_matchup(red_policy="random", black_policy="random", num_games=50)
  run_matchup(red_policy="greedy", black_policy="ai", num_games=50)
  run_matchup(red_policy="greedy", black_policy="random", num_games=50)


if __name__ == "__main__":
  main()
