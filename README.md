# Knight's Tour Memory Trainer

This repository provides a small Python application that helps you learn and
rehearse a complete Knight's Tour on a standard 8×8 chessboard.  The script uses
Warnsdorff's heuristic to build a deterministic tour and includes tooling to:

- list the tour moves in forward or reverse order,
- render the board with move numbers so you can study the path visually, and
- run an interactive quiz that checks your ability to recall the sequence.

## Requirements

- Python 3.10 or newer (for type annotations such as ``list[tuple[int, int]]``)
- Optional: ``pytest`` if you would like to run the automated tests.

## Usage

```bash
python knight_tour_trainer.py show --reverse          # Print the reversed move list
python knight_tour_trainer.py board --steps 16         # Visualise the first 16 moves
python knight_tour_trainer.py quiz --reverse           # Practice recalling the path
```

Moves are reported using algebraic notation.  For example ``a1`` is the bottom
left corner when the board is viewed from White's perspective.

## Running Tests

Install the test dependency and execute ``pytest``:

```bash
pip install pytest
pytest
```

The test suite verifies that the generated tour is valid and that helper
utilities such as the board renderer behave as expected.
