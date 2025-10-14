import pathlib
import sys

# Ensure the project root (which contains knight_tour_trainer.py) is importable
ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
