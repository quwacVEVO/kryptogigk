"""Uruchom pełny, odtwarzalny zestaw eksperymentów laboratorium 5."""

from pathlib import Path

from lab05.experiment import run_all


if __name__ == "__main__":
    root = Path(__file__).resolve().parent
    run_all(root)
    print(f"Zapisano dane i wyniki w: {root / 'results'}")
