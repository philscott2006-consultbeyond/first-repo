"""Knight's Tour memory trainer.

This module provides utilities to generate a Knight's Tour on a standard
chessboard and a lightweight command line tool that helps memorise the tour in
reverse order.  The default implementation uses Warnsdorff's rule to compute a
deterministic tour that can be reproduced on every run.  The tour can then be
presented on an ASCII board, streamed step-by-step, or rehearsed via a simple
quiz loop.

Example
-------
Display the first five reversed moves on the board::

    python knight_tour_trainer.py board --steps 5 --reverse

Run an interactive recall quiz::

    python knight_tour_trainer.py quiz --reverse

The script intentionally keeps dependencies minimal so that it can be executed
from any standard Python installation.
"""

from __future__ import annotations

import argparse
import itertools
import sys
from typing import Iterator, List, Optional, Sequence, Tuple


BOARD_SIZE: int = 8
"""The length of one side of the chessboard."""

Move = Tuple[int, int]


def _is_on_board(square: Move) -> bool:
    """Return ``True`` if *square* lies inside the chessboard boundaries."""

    row, col = square
    return 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE


def _knight_moves(square: Move) -> Iterator[Move]:
    """Yield all potential knight moves from *square* without bounds checks."""

    row, col = square
    offsets = (
        (2, 1),
        (1, 2),
        (-1, 2),
        (-2, 1),
        (-2, -1),
        (-1, -2),
        (1, -2),
        (2, -1),
    )
    for d_row, d_col in offsets:
        yield row + d_row, col + d_col


def _count_onward_moves(square: Move, visited: set[Move]) -> int:
    """Count valid onward moves for Warnsdorff's heuristic."""

    return sum(1 for nxt in _knight_moves(square) if _is_on_board(nxt) and nxt not in visited)


def generate_knights_tour(start: Move = (0, 0)) -> List[Move]:
    """Generate a complete Knight's Tour using Warnsdorff's rule.

    Parameters
    ----------
    start:
        The initial square for the tour expressed in zero-indexed coordinates
        ``(row, column)``.

    Returns
    -------
    list[tuple[int, int]]
        The ordered list of 64 moves covering every square exactly once.

    Raises
    ------
    RuntimeError
        If a complete tour cannot be produced (unlikely on a standard board).
    """

    path: List[Move] = [start]
    visited: set[Move] = {start}

    for _ in range(BOARD_SIZE * BOARD_SIZE - 1):
        current = path[-1]
        candidates = [
            nxt
            for nxt in _knight_moves(current)
            if _is_on_board(nxt) and nxt not in visited
        ]

        if not candidates:
            break

        # Apply Warnsdorff's rule: prefer moves with the fewest onward options.
        next_move = min(
            candidates,
            key=lambda move: (_count_onward_moves(move, visited | {move}), move),
        )

        visited.add(next_move)
        path.append(next_move)

    if len(path) != BOARD_SIZE * BOARD_SIZE:
        raise RuntimeError("Failed to construct a full Knight's Tour path")

    return path


def algebraic(square: Move) -> str:
    """Convert a coordinate ``(row, column)`` to algebraic notation (``"a1"``)."""

    row, col = square
    return f"{chr(ord('a') + col)}{row + 1}"


def reversed_tour(path: Sequence[Move]) -> List[Move]:
    """Return a copy of *path* in reverse order."""

    return list(reversed(path))


def format_board(path: Sequence[Move], upto: Optional[int] = None) -> str:
    """Return an ASCII representation of the tour.

    Parameters
    ----------
    path:
        The ordered tour to display.
    upto:
        Optional number of steps to show.  If provided, only moves strictly
        before this index are included, allowing incremental visualisation.
    """

    board = [["." for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
    upto = len(path) if upto is None else max(0, min(upto, len(path)))

    for move_index, square in enumerate(itertools.islice(path, upto)):
        row, col = square
        board[row][col] = str(move_index + 1)

    lines = ["  a  b  c  d  e  f  g  h"]
    for row_index, row in enumerate(board[::-1]):
        rank = BOARD_SIZE - row_index
        padded = [value.rjust(2) for value in row]
        lines.append(f"{rank} {' '.join(padded)}")
    lines.append("  a  b  c  d  e  f  g  h")
    return "\n".join(lines)


def _print_sequence(path: Sequence[Move], steps: Optional[int], stream) -> None:
    upto = len(path) if steps is None else max(0, min(steps, len(path)))
    for index, square in enumerate(itertools.islice(path, upto), start=1):
        print(f"{index:02d}: {algebraic(square)}", file=stream)


def _run_quiz(path: Sequence[Move]) -> int:
    """Interactive recall quiz.  Returns the score the learner achieved."""

    print(
        "Enter the square for each move in algebraic notation (e.g. 'e4').",
        "Type 'quit' to stop early.\n",
        sep="\n",
    )

    score = 0
    for index, square in enumerate(path, start=1):
        answer = input(f"Move {index:02d}: ").strip().lower()
        if answer in {"quit", "exit"}:
            break
        if answer == algebraic(square):
            print("  ✓ Correct!\n")
            score += 1
        else:
            print(f"  ✗ The correct square was {algebraic(square)}.\n")
    print(f"You recalled {score} move(s) correctly.")
    return score


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--reverse",
        action="store_true",
        help="work with the tour in reverse order",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    show_parser = subparsers.add_parser("show", help="print the move list")
    show_parser.add_argument(
        "--steps",
        type=int,
        help="limit the number of moves displayed",
    )

    board_parser = subparsers.add_parser("board", help="render the tour on a board")
    board_parser.add_argument(
        "--steps",
        type=int,
        help="limit the number of moves rendered",
    )

    subparsers.add_parser("quiz", help="recall the moves interactively")

    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    forward_tour = generate_knights_tour()
    path = reversed_tour(forward_tour) if args.reverse else forward_tour

    if args.command == "show":
        _print_sequence(path, args.steps, sys.stdout)
        return 0

    if args.command == "board":
        print(format_board(path, args.steps))
        return 0

    if args.command == "quiz":
        _run_quiz(path)
        return 0

    parser.error("Unknown command")
    return 2


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main())
