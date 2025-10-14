import itertools

import pytest

import knight_tour_trainer as ktt


def test_tour_covers_every_square():
    tour = ktt.generate_knights_tour()
    assert len(tour) == ktt.BOARD_SIZE ** 2
    assert len(set(tour)) == ktt.BOARD_SIZE ** 2


@pytest.mark.parametrize("a, b", [((0, 0), (1, 2)), ((3, 3), (4, 5)), ((7, 7), (6, 5))])
def test_algebraic_round_trip_examples(a, b):
    # Ensure algebraic conversion is stable for a few coordinates.
    assert ktt.algebraic(a) != ktt.algebraic(b)


def test_tour_moves_are_valid_knight_steps():
    tour = ktt.generate_knights_tour()
    for current, nxt in itertools.pairwise(tour):
        row_diff = abs(current[0] - nxt[0])
        col_diff = abs(current[1] - nxt[1])
        assert sorted((row_diff, col_diff)) == [1, 2]


def test_reversed_tour_has_reverse_order():
    tour = ktt.generate_knights_tour()
    reversed_path = ktt.reversed_tour(tour)
    assert reversed_path == list(reversed(tour))


def test_board_formatter_renders_requested_steps():
    tour = [(0, 0), (1, 2), (2, 4)]
    board = ktt.format_board(tour, upto=2)
    interior_rows = [line.split()[1:] for line in board.splitlines()[1:-1]]
    # The first two moves should be labelled while the third remains '.'
    assert "1" in interior_rows[-1]
    assert "2" in interior_rows[-2]
    assert all(cell != "3" for row in interior_rows for cell in row)
