"""Niezależna kontrola spójności zapisanych danych i tabel wynikowych."""

from __future__ import annotations

import csv
import statistics
from pathlib import Path

from lab05.generators import collision_stats, lcg_cycle_info, lfsr_cycle_info
from lab05.io_utils import read_integer_file
from lab05.primality import prime_division_test


ROOT = Path(__file__).resolve().parent


def read_csv(name: str) -> list[dict[str, str]]:
    with (ROOT / "results" / name).open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def verify_generator_rows() -> None:
    summaries = {row["generator"]: row for row in read_csv("generator_summary.csv")}
    inputs = {
        "LFSR": read_integer_file(ROOT / "data" / "lfsr_numbers.txt"),
        "LCG": read_integer_file(ROOT / "data" / "lcg_numbers.txt"),
    }
    cycles = {
        "LFSR": lfsr_cycle_info(
            16,
            (0, 2, 3, 5),
            (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1),
        ),
        "LCG": lcg_cycle_info(65_536, 5, 1, 20_226),
    }
    for source, values in inputs.items():
        if len(values) != 200 or not all(10_000 <= value <= 59_999 for value in values):
            raise AssertionError(f"Niepoprawne dane główne dla {source}.")
        if len(values) > 59_999 - 10_000 + 1:
            raise AssertionError("Naruszono konieczny warunek K <= b-a+1.")
        stats = collision_stats(values)
        row = summaries[source]
        expected = {
            "count": stats.count,
            "unique_count": stats.unique_count,
            "duplicate_occurrences": stats.duplicate_occurrences,
            "repeated_values": stats.repeated_values,
            "colliding_pairs": stats.colliding_pairs,
            "state_preperiod": cycles[source].preperiod,
            "state_period": cycles[source].period,
        }
        for field, value in expected.items():
            if int(row[field]) != value:
                raise AssertionError(f"Niezgodność {source}.{field}: {row[field]} != {value}")


def verify_primality_tables() -> None:
    measurements = read_csv("primality_measurements.csv")
    if len(measurements) != 1_200:
        raise AssertionError(f"Oczekiwano 1200 pomiarów, otrzymano {len(measurements)}.")
    for row in measurements:
        number = int(row["number"])
        truth = int(prime_division_test(number))
        if int(row["truth"]) != truth:
            raise AssertionError(f"Błędny status dokładny dla {number}.")
        if int(row["elapsed_ns"]) < 0:
            raise AssertionError("Ujemny czas pomiaru.")

    summary_rows = read_csv("primality_summary.csv")
    for summary in summary_rows:
        selected = [
            int(row["elapsed_ns"])
            for row in measurements
            if row["source"] == summary["source"] and row["method"] == summary["method"]
        ]
        expected = {
            "measurements": len(selected),
            "min_ns": min(selected),
            "max_ns": max(selected),
            "mean_ns": round(statistics.fmean(selected), 2),
            "median_ns": round(statistics.median(selected), 2),
        }
        for field, value in expected.items():
            recorded = float(summary[field]) if field in {"mean_ns", "median_ns"} else int(summary[field])
            if recorded != value:
                raise AssertionError(
                    f"Niezgodna statystyka {summary['source']}/{summary['method']}/{field}."
                )

    error_rows = read_csv("error_summary.csv")
    for summary in error_rows:
        selected = [
            row
            for row in measurements
            if row["source"] == summary["source"] and row["method"] == summary["method"]
        ]
        false_primes = sum(row["result"] == "1" and row["truth"] == "0" for row in selected)
        false_composites = sum(row["result"] == "0" and row["truth"] == "1" for row in selected)
        if int(summary["false_primes"]) != false_primes:
            raise AssertionError("Niezgodna liczba false_primes.")
        if int(summary["false_composites"]) != false_composites:
            raise AssertionError("Niezgodna liczba false_composites.")


def main() -> None:
    verify_generator_rows()
    verify_primality_tables()
    print("OK: dane, cykle, statusy pierwszości i statystyki CSV są spójne.")


if __name__ == "__main__":
    main()
