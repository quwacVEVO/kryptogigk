"""Odtwarzalne eksperymenty i zapis tabel do CSV/JSON/Markdown."""

from __future__ import annotations

import csv
import json
import platform
import statistics
from dataclasses import asdict
from pathlib import Path
from random import Random
from time import perf_counter_ns
from typing import Callable, Iterable

from .generators import (
    LCG,
    LFSR,
    collision_stats,
    has_full_lcg_period,
    hull_dobell_conditions,
    lcg_cycle_info,
    lfsr_cycle_info,
)
from .io_utils import read_integer_file, write_integer_file
from .primality import fermat_test, miller_rabin_test, prime_division_test


MAIN_K = 200
MAIN_LOWER = 10_000
MAIN_UPPER = 59_999
LFSR_MAIN = {
    "length": 16,
    "taps": (0, 2, 3, 5),
    "seed": (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1),
}
LCG_MAIN = {"modulus": 65_536, "multiplier": 5, "increment": 1, "seed": 20_226}
FERMAT_ITERATIONS = 5
MR_ITERATIONS = 5
RANDOM_SEED = 20_261_122


def _write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        raise ValueError(f"Brak wierszy do zapisania w {path}.")
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def _time_call(function: Callable[[], bool]) -> tuple[bool, int]:
    start = perf_counter_ns()
    result = function()
    return result, perf_counter_ns() - start


def _benchmark_primality(source: str, values: Iterable[int]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    fermat_rng = Random(RANDOM_SEED + (1 if source == "LFSR" else 2))
    mr_rng = Random(RANDOM_SEED + (3 if source == "LFSR" else 4))
    for index, number in enumerate(values):
        exact_result, exact_ns = _time_call(lambda n=number: prime_division_test(n))
        fermat_result, fermat_ns = _time_call(
            lambda n=number: fermat_test(n, FERMAT_ITERATIONS, fermat_rng)
        )
        mr_result, mr_ns = _time_call(
            lambda n=number: miller_rabin_test(n, MR_ITERATIONS, mr_rng)
        )
        for method, result, elapsed in (
            ("dzielenie_przez_pierwsze", exact_result, exact_ns),
            ("Fermat", fermat_result, fermat_ns),
            ("Miller-Rabin", mr_result, mr_ns),
        ):
            rows.append(
                {
                    "source": source,
                    "index": index,
                    "number": number,
                    "method": method,
                    "result": int(result),
                    "truth": int(exact_result),
                    "elapsed_ns": elapsed,
                }
            )
    return rows


def _timing_summary(measurements: list[dict[str, object]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    keys = sorted({(str(row["source"]), str(row["method"])) for row in measurements})
    for source, method in keys:
        times = [
            int(row["elapsed_ns"])
            for row in measurements
            if row["source"] == source and row["method"] == method
        ]
        rows.append(
            {
                "source": source,
                "method": method,
                "measurements": len(times),
                "min_ns": min(times),
                "max_ns": max(times),
                "mean_ns": round(statistics.fmean(times), 2),
                "median_ns": round(statistics.median(times), 2),
            }
        )
    return rows


def _error_summary(measurements: list[dict[str, object]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    keys = sorted({(str(row["source"]), str(row["method"])) for row in measurements})
    for source, method in keys:
        selected = [
            row
            for row in measurements
            if row["source"] == source and row["method"] == method
        ]
        rows.append(
            {
                "source": source,
                "method": method,
                "measurements": len(selected),
                "false_primes": sum(
                    int(row["result"] == 1 and row["truth"] == 0) for row in selected
                ),
                "false_composites": sum(
                    int(row["result"] == 0 and row["truth"] == 1) for row in selected
                ),
            }
        )
    return rows


def _lfsr_parameter_rows() -> list[dict[str, object]]:
    configs = [
        ("n3_dobre", 3, (0, 1), (0, 0, 1)),
        ("n4_dobre", 4, (0, 1), (0, 0, 0, 1)),
        ("n4_inne_ziarno", 4, (0, 1), (1, 0, 0, 0)),
        ("n4_slabe_odczepy", 4, (0,), (0, 0, 0, 1)),
        ("n8_dobre", 8, (0, 2, 3, 4), (0, 0, 0, 0, 0, 0, 0, 1)),
        ("n16_dobre", 16, (0, 2, 3, 5), LFSR_MAIN["seed"]),
        ("n16_ziarno_zerowe", 16, (0, 2, 3, 5), (0,) * 16),
    ]
    rows: list[dict[str, object]] = []
    for name, length, taps, seed in configs:
        cycle = lfsr_cycle_info(length, taps, seed, max_steps=200_000)
        values = LFSR(length, taps, seed).generate(200, 0, 255)
        collisions = collision_stats(values)
        rows.append(
            {
                "generator": "LFSR",
                "configuration": name,
                "parameters": f"n={length}; taps={taps}; seed={''.join(map(str, seed))}",
                "state_preperiod": cycle.preperiod,
                "state_period": cycle.period,
                "K": collisions.count,
                "unique_values": collisions.unique_count,
                "duplicate_occurrences": collisions.duplicate_occurrences,
                "colliding_pairs": collisions.colliding_pairs,
            }
        )
    return rows


def _lcg_parameter_rows() -> list[dict[str, object]]:
    configs = [
        ("pelny_okres", 256, 5, 1, 7),
        ("pelny_okres_inne_ziarno", 256, 5, 1, 8),
        ("slaby_mnoznik", 256, 6, 1, 7),
        ("parzysty_przyrost", 256, 5, 2, 7),
        ("mniejszy_modul", 64, 5, 1, 7),
    ]
    rows: list[dict[str, object]] = []
    for name, modulus, multiplier, increment, seed in configs:
        cycle = lcg_cycle_info(modulus, multiplier, increment, seed, max_steps=10_000)
        generator = LCG(modulus, multiplier, increment, seed)
        values = [generator.step() for _ in range(200)]
        collisions = collision_stats(values)
        rows.append(
            {
                "generator": "LCG",
                "configuration": name,
                "parameters": (
                    f"m={modulus}; a={multiplier}; c={increment}; x0={seed}; "
                    f"Hull-Dobell={has_full_lcg_period(modulus, multiplier, increment)}"
                ),
                "state_preperiod": cycle.preperiod,
                "state_period": cycle.period,
                "K": collisions.count,
                "unique_values": collisions.unique_count,
                "duplicate_occurrences": collisions.duplicate_occurrences,
                "colliding_pairs": collisions.colliding_pairs,
            }
        )
    return rows


def _range_comparison() -> list[dict[str, object]]:
    scenarios = [
        ("3_cyfry", 100, 999, 1_024),
        ("5_cyfr", 10_000, 99_999, 131_072),
        ("7_cyfr", 1_000_000, 9_999_999, 16_777_216),
    ]
    rows: list[dict[str, object]] = []
    for scenario, lower, upper, modulus in scenarios:
        lfsr_values = LFSR(**LFSR_MAIN).generate(100, lower, upper)
        lcg_values = LCG(modulus, 5, 1, RANDOM_SEED % modulus).generate(
            100, lower, upper
        )
        for source, values in (("LFSR", lfsr_values), ("LCG", lcg_values)):
            measurements = _benchmark_primality(source, values)
            for summary in _timing_summary(measurements):
                rows.append(
                    {
                        "scenario": scenario,
                        "lower": lower,
                        "upper": upper,
                        **summary,
                    }
                )
    return rows


def _mr_iteration_analysis(values: list[int]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    truths = [prime_division_test(value) for value in values]
    for iterations in (1, 3, 5, 10):
        rng = Random(RANDOM_SEED + iterations)
        times: list[int] = []
        results: list[bool] = []
        for number in values:
            result, elapsed = _time_call(
                lambda n=number: miller_rabin_test(n, iterations, rng)
            )
            results.append(result)
            times.append(elapsed)
        rows.append(
            {
                "iterations": iterations,
                "measurements": len(values),
                "min_ns": min(times),
                "max_ns": max(times),
                "mean_ns": round(statistics.fmean(times), 2),
                "median_ns": round(statistics.median(times), 2),
                "false_primes": sum(r and not t for r, t in zip(results, truths)),
                "false_composites": sum(not r and t for r, t in zip(results, truths)),
            }
        )
    return rows


def _markdown_table(rows: list[dict[str, object]], columns: list[str]) -> str:
    header = "| " + " | ".join(columns) + " |"
    separator = "| " + " | ".join("---" for _ in columns) + " |"
    body = [
        "| " + " | ".join(str(row[column]) for column in columns) + " |"
        for row in rows
    ]
    return "\n".join([header, separator, *body])


def run_all(project_root: Path) -> None:
    data_dir = project_root / "data"
    results_dir = project_root / "results"
    data_dir.mkdir(parents=True, exist_ok=True)
    results_dir.mkdir(parents=True, exist_ok=True)

    lfsr_values = LFSR(**LFSR_MAIN).generate(MAIN_K, MAIN_LOWER, MAIN_UPPER)
    lcg_values = LCG(**LCG_MAIN).generate(MAIN_K, MAIN_LOWER, MAIN_UPPER)
    write_integer_file(data_dir / "lfsr_numbers.txt", lfsr_values)
    write_integer_file(data_dir / "lcg_numbers.txt", lcg_values)
    if read_integer_file(data_dir / "lfsr_numbers.txt") != lfsr_values:
        raise RuntimeError("Kontrola ponownego odczytu LFSR nie powiodła się.")
    if read_integer_file(data_dir / "lcg_numbers.txt") != lcg_values:
        raise RuntimeError("Kontrola ponownego odczytu LCG nie powiodła się.")

    lfsr_cycle = lfsr_cycle_info(**LFSR_MAIN, max_steps=200_000)
    lcg_cycle = lcg_cycle_info(**LCG_MAIN, max_steps=100_000)
    lfsr_collisions = collision_stats(lfsr_values)
    lcg_collisions = collision_stats(lcg_values)
    generator_summary = [
        {
            "generator": "LFSR",
            "K": MAIN_K,
            "lower": MAIN_LOWER,
            "upper": MAIN_UPPER,
            "state_preperiod": lfsr_cycle.preperiod,
            "state_period": lfsr_cycle.period,
            **asdict(lfsr_collisions),
        },
        {
            "generator": "LCG",
            "K": MAIN_K,
            "lower": MAIN_LOWER,
            "upper": MAIN_UPPER,
            "state_preperiod": lcg_cycle.preperiod,
            "state_period": lcg_cycle.period,
            **asdict(lcg_collisions),
        },
    ]
    _write_csv(results_dir / "generator_summary.csv", generator_summary)

    parameter_rows = _lfsr_parameter_rows() + _lcg_parameter_rows()
    _write_csv(results_dir / "parameter_analysis.csv", parameter_rows)

    measurements = _benchmark_primality("LFSR", lfsr_values)
    measurements += _benchmark_primality("LCG", lcg_values)
    timing_rows = _timing_summary(measurements)
    error_rows = _error_summary(measurements)
    _write_csv(results_dir / "primality_measurements.csv", measurements)
    _write_csv(results_dir / "primality_summary.csv", timing_rows)
    _write_csv(results_dir / "error_summary.csv", error_rows)

    range_rows = _range_comparison()
    _write_csv(results_dir / "range_comparison.csv", range_rows)
    mr_rows = _mr_iteration_analysis(lfsr_values + lcg_values)
    _write_csv(results_dir / "mr_iterations.csv", mr_rows)

    metadata = {
        "python": platform.python_version(),
        "platform": platform.platform(),
        "processor": platform.processor() or "not reported by platform.processor()",
        "timer": "time.perf_counter_ns",
        "timer_unit": "ns",
        "K": MAIN_K,
        "interval": [MAIN_LOWER, MAIN_UPPER],
        "lfsr": {
            "representation": "oldest bit on left; output state[0]; shift left",
            **LFSR_MAIN,
        },
        "lcg": LCG_MAIN,
        "lcg_hull_dobell": hull_dobell_conditions(
            LCG_MAIN["modulus"], LCG_MAIN["multiplier"], LCG_MAIN["increment"]
        ),
        "fermat_iterations": FERMAT_ITERATIONS,
        "miller_rabin_iterations": MR_ITERATIONS,
        "random_seed": RANDOM_SEED,
        "mapping": "rejection sampling; no modulo bias",
        "duplicate_timing_policy": "every position is timed, including duplicates",
    }
    (results_dir / "run_metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    report = f"""# Wyniki odtwarzalnego przebiegu

## Scenariusz główny

- `K = {MAIN_K}`, przedział `[{MAIN_LOWER}, {MAIN_UPPER}]`.
- LFSR: `n={LFSR_MAIN['length']}`, odczepy 0-based `{LFSR_MAIN['taps']}`, ziarno `{''.join(map(str, LFSR_MAIN['seed']))}`.
- LCG: `m={LCG_MAIN['modulus']}`, `a={LCG_MAIN['multiplier']}`, `c={LCG_MAIN['increment']}`, `x0={LCG_MAIN['seed']}`.
- Mapowanie: rejection sampling, zatem bez obciążenia wynikającego z prostego modulo.
- Czasy obejmują wyłącznie pojedyncze wywołanie testu i są mierzone `perf_counter_ns`.

## Generatory

{_markdown_table(generator_summary, ['generator', 'K', 'unique_count', 'duplicate_occurrences', 'colliding_pairs', 'state_preperiod', 'state_period'])}

`duplicate_occurrences = K - liczba różnych wartości`. `colliding_pairs` to suma `c*(c-1)/2` po licznościach każdej wartości. Okres dotyczy pełnego stanu generatora, a nie ciągu po mapowaniu.

## Czasy testów pierwszości

{_markdown_table(timing_rows, ['source', 'method', 'measurements', 'min_ns', 'max_ns', 'mean_ns', 'median_ns'])}

## Błędne decyzje względem dokładnego dzielenia przez liczby pierwsze

{_markdown_table(error_rows, ['source', 'method', 'measurements', 'false_primes', 'false_composites'])}

Poprawnie zaimplementowane testy Fermata i Millera-Rabina nie powinny odrzucać liczb pierwszych, dlatego oczekiwano zera w kolumnie `false_composites`. Testy probabilistyczne nie są dowodem pierwszości; brak błędów w tym ograniczonym zbiorze nie gwarantuje ich braku poza nim.

## Wpływ liczby iteracji Millera-Rabina

{_markdown_table(mr_rows, ['iterations', 'measurements', 'mean_ns', 'median_ns', 'false_primes', 'false_composites'])}

## Interpretacja

Dokładny test dzielenia jest punktem odniesienia i dla tego małego zakresu pozostaje praktyczny. Fermat może zostać oszukany przez pseudopierwsze i liczby Carmichaela, co pokazują testy jednostkowe z liczbą 561. Miller-Rabin daje lepszy kompromis dla większych liczb, lecz jego wynik nadal należy opisywać jako prawdopodobną pierwszość. Różnice bardzo krótkich czasów są podatne na szum systemowy; surowe pomiary zachowano w `primality_measurements.csv`.
"""
    (results_dir / "REPORT_RESULTS.md").write_text(report, encoding="utf-8")
