"""Prosty, jawny format plików: jedna liczba całkowita w każdym wierszu."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable


def write_integer_file(path: str | Path, values: Iterable[int]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    materialized = list(values)
    if any(not isinstance(value, int) for value in materialized):
        raise TypeError("Do pliku można zapisać wyłącznie liczby całkowite.")
    target.write_text("".join(f"{value}\n" for value in materialized), encoding="utf-8")


def read_integer_file(path: str | Path) -> list[int]:
    source = Path(path)
    if not source.exists():
        raise FileNotFoundError(f"Nie znaleziono pliku: {source}")
    values: list[int] = []
    for line_number, raw_line in enumerate(source.read_text(encoding="utf-8").splitlines(), 1):
        text = raw_line.strip()
        if not text:
            raise ValueError(f"Pusty wiersz w linii {line_number} pliku {source}.")
        try:
            values.append(int(text))
        except ValueError as exc:
            raise ValueError(
                f"Niepoprawna liczba całkowita w linii {line_number}: {text!r}."
            ) from exc
    return values
