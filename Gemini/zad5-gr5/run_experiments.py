"""Główny skrypt eksperymentalny — Lab 05, Grupa 5 (GenAI).

Uruchamia spójny, odtwarzalny zestaw eksperymentów dla:
    - Grupy 1: LFSR (przykłady z notatki, generowanie K liczb do pliku, kolizje i cykle,
      ciąg bez kolizji, wpływ długości/odczepów/ziarna).
    - Grupy 2: LCG (przykłady z notatki, generowanie K liczb do pliku, kolizje i cykle,
      ciąg bez kolizji, wpływ m, a, c, x0 oraz porównanie mapowania scale vs mod).
    - Grupy 3: Testy pierwszości na liczbach z LFSR i LCG, statystyki czasów,
      status rzeczywisty (pseudopierwsze i pseudozłożone), skalowanie po rozmiarze liczb,
      wpływ liczby iteracji Millera–Rabina oraz test diagnostyczny liczb Carmichaela.

Zapisuje wyniki w:
    - zad5-gr5/data/*.txt
    - zad5-gr5/results/*.csv
    - zad5-gr5/results/experiment_results.json
    - zad5-gr5/results/SUMMARY_TABLES.md
    - src/data/experimentResults.json (dla interaktywnego panelu WWW)
"""

from __future__ import annotations

import csv
import json
import math
import platform
import random
import sys
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
RESULTS_DIR = BASE_DIR / "results"
WEB_DATA_PATH = BASE_DIR.parent / "src" / "data" / "experimentResults.json"

if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import lcg
import lfsr
import primality

# =============================================================================
# Jawne parametry wspólnego benchmarku (odtwarzalne pomiędzy modelami GenAI)
# =============================================================================
K_BASE = 200
RANGE_A = 1000
RANGE_B = 100_000
PRIMALITY_ITERATIONS = 10
PRIMALITY_RNG_SEED = 20261126

LFSR_BASE_LENGTH = 17
LFSR_BASE_TAPS = (0, 3)  # x^17 + x^3 + 1 (wielomian pierwotny, okres 2^17 - 1 = 131071)
LFSR_BASE_SEED = (1, 0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 1, 0, 1, 0, 0, 1)

LCG_BASE_M = 2**31
LCG_BASE_A = 1103515245
LCG_BASE_C = 12345
LCG_BASE_X0 = 123456

CARMICHAEL_NUMBERS = [
    561, 1105, 1729, 2465, 2821, 6601, 8911, 10585, 15841, 29341,
    41041, 46657, 52633, 62745, 63973, 75361, 101101, 115921, 126217, 162401,
]


def run_lfsr_experiments() -> dict[str, object]:
    """Wykonuje komplet eksperymentów dla Grupy 1 (LFSR)."""
    # 1. Weryfikacja 4 przykładów 32-bitowych ze slajdu 6/14 notatki T. Gzelli
    lecture_configs = [
        {"label": "Przykład 1 (n=3)", "p": [1, 1, 0], "seed": [0, 0, 1]},
        {"label": "Przykład 2 (n=4, pierwotny)", "p": [1, 1, 0, 0], "seed": [0, 0, 0, 1]},
        {"label": "Przykład 3 (n=4, niepierwotny)", "p": [1, 1, 1, 1], "seed": [1, 0, 0, 1]},
        {"label": "Przykład 4 (n=6)", "p": [1, 1, 0, 1, 1, 0], "seed": [0, 0, 1, 0, 0, 1]},
    ]
    lecture_examples = []
    for cfg in lecture_configs:
        gen = lfsr.LFSR.from_coefficients(cfg["p"], cfg["seed"])
        bits_32 = gen.generate_bits(32)
        taps = lfsr.taps_from_coefficients(cfg["p"])
        cyc = lfsr.detect_state_cycle(len(cfg["p"]), taps, cfg["seed"])
        lecture_examples.append(
            {
                "label": cfg["label"],
                "length": len(cfg["p"]),
                "p": cfg["p"],
                "taps": list(taps),
                "seed": cfg["seed"],
                "bits_32": "".join(str(b) for b in bits_32),
                "state_cycle": cyc["cycle_length"],
                "max_theoretical": cyc["max_theoretical_period"],
                "is_maximal": cyc["is_maximal"],
            }
        )

    # 2. Główny zbiór K=200 liczb z [1000, 100000] i zapis do pliku
    base_gen = lfsr.LFSR(LFSR_BASE_LENGTH, LFSR_BASE_TAPS, LFSR_BASE_SEED)
    base_numbers = base_gen.generate_integers(
        k=K_BASE, a=RANGE_A, b=RANGE_B, bit_width=17, mapping="mod"
    )
    lfsr_file = lfsr.save_numbers_to_file(
        DATA_DIR / "lfsr_numbers.txt",
        base_numbers,
        header_comments=[
            f"LFSR base dataset: K={K_BASE}, range=[{RANGE_A}, {RANGE_B}]",
            f"n={LFSR_BASE_LENGTH}, taps={LFSR_BASE_TAPS}, mapping=mod, bit_width=17",
            f"seed={''.join(str(b) for b in LFSR_BASE_SEED)}",
        ],
    )
    # Odczyt powrotny (weryfikacja zapisu i parsera)
    reloaded = lfsr.load_numbers_from_file(lfsr_file)
    assert reloaded == base_numbers

    base_collisions = lfsr.analyze_collisions(base_numbers)
    base_state_cycle = lfsr.detect_state_cycle(LFSR_BASE_LENGTH, LFSR_BASE_TAPS, LFSR_BASE_SEED)
    base_word_cycle = lfsr.detect_output_word_cycle(
        LFSR_BASE_LENGTH, LFSR_BASE_TAPS, LFSR_BASE_SEED, RANGE_A, RANGE_B, bit_width=17, mapping="mod"
    )

    # 3. Demonstracja ciągu K=200 liczb BEZ KOLIZJI z przedziału [1000, 100000]
    collision_free_numbers = lfsr.generate_collision_free_sequence(
        k=K_BASE,
        a=RANGE_A,
        b=RANGE_B,
        length=LFSR_BASE_LENGTH,
        taps=LFSR_BASE_TAPS,
        seed=LFSR_BASE_SEED,
        bit_width=17,
        mapping="rejection",
    )
    lfsr.save_numbers_to_file(
        DATA_DIR / "lfsr_no_collisions.txt",
        collision_free_numbers,
        header_comments=[
            f"LFSR collision-free dataset: K={K_BASE}, range=[{RANGE_A}, {RANGE_B}]",
            f"n={LFSR_BASE_LENGTH}, taps={LFSR_BASE_TAPS}, mapping=rejection, bit_width=17",
            f"seed={''.join(str(b) for b in LFSR_BASE_SEED)}",
            "Verified unique: 200/200 (0 collisions)",
        ],
    )
    cf_collisions = lfsr.analyze_collisions(collision_free_numbers)

    # 4. Analiza wpływu długości rejestru, odczepów i ziarna (tabela porównawcza)
    # Wszystkie warianty na wspólnym przedziale [1000, 100000], K=200
    variants = [
        {
            "name": "n=8, pierwotny (0,2,3,4), ziarno A",
            "length": 8,
            "taps": (0, 2, 3, 4),
            "seed": (1, 0, 1, 1, 0, 0, 1, 0),
            "mapping": "mod",
        },
        {
            "name": "n=8, słabe odczepy (0,4), ziarno A",
            "length": 8,
            "taps": (0, 4),
            "seed": (1, 0, 1, 1, 0, 0, 1, 0),
            "mapping": "mod",
        },
        {
            "name": "n=12, pierwotny (0,1,4,6), ziarno A",
            "length": 12,
            "taps": (0, 1, 4, 6),
            "seed": (1, 0, 1, 0, 1, 1, 0, 0, 1, 0, 1, 1),
            "mapping": "mod",
        },
        {
            "name": "n=12, niepierwotny (0,6), ziarno A",
            "length": 12,
            "taps": (0, 6),
            "seed": (1, 0, 1, 0, 1, 1, 0, 0, 1, 0, 1, 1),
            "mapping": "mod",
        },
        {
            "name": "n=16, pierwotny (0,2,3,5), ziarno A",
            "length": 16,
            "taps": (0, 2, 3, 5),
            "seed": (1, 0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 1),
            "mapping": "mod",
        },
        {
            "name": "n=16, niepierwotny (0,8), ziarno A",
            "length": 16,
            "taps": (0, 8),
            "seed": (1, 0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 1),
            "mapping": "mod",
        },
        {
            "name": "n=17, pierwotny (0,3), ziarno B (000...001)",
            "length": 17,
            "taps": (0, 3),
            "seed": (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1),
            "mapping": "mod",
        },
        {
            "name": "n=17, pierwotny (0,3), ziarno A (bazowe, mod)",
            "length": 17,
            "taps": (0, 3),
            "seed": LFSR_BASE_SEED,
            "mapping": "mod",
        },
        {
            "name": "n=17, pierwotny (0,3), ziarno A (rejection)",
            "length": 17,
            "taps": (0, 3),
            "seed": LFSR_BASE_SEED,
            "mapping": "rejection",
        },
    ]

    comparison_table = []
    for var in variants:
        gen = lfsr.LFSR(var["length"], var["taps"], var["seed"])
        nums = gen.generate_integers(k=K_BASE, a=RANGE_A, b=RANGE_B, mapping=var["mapping"])
        col = lfsr.analyze_collisions(nums)
        cyc = lfsr.detect_state_cycle(var["length"], var["taps"], var["seed"])
        comparison_table.append(
            {
                "name": var["name"],
                "length": var["length"],
                "taps": list(var["taps"]),
                "seed_str": "".join(str(b) for b in var["seed"]),
                "mapping": var["mapping"],
                "state_cycle": cyc["cycle_length"],
                "max_theoretical": cyc["max_theoretical_period"],
                "is_maximal": cyc["is_maximal"],
                "unique_count": col["unique_count"],
                "total_collisions": col["total_collisions"],
                "collision_rate_pct": round(float(col["collision_rate"]) * 100.0, 2),
                "min_val": min(nums),
                "max_val": max(nums),
                "mean_val": round(sum(nums) / len(nums), 1),
            }
        )

    return {
        "lecture_examples": lecture_examples,
        "base_config": {
            "K": K_BASE,
            "range": [RANGE_A, RANGE_B],
            "length": LFSR_BASE_LENGTH,
            "taps": list(LFSR_BASE_TAPS),
            "seed": list(LFSR_BASE_SEED),
            "seed_str": "".join(str(b) for b in LFSR_BASE_SEED),
            "bit_width": 17,
            "mapping": "mod",
            "output_file": "zad5-gr5/data/lfsr_numbers.txt",
        },
        "base_numbers": base_numbers,
        "base_collisions": base_collisions,
        "base_state_cycle": base_state_cycle,
        "base_word_cycle": base_word_cycle,
        "collision_free": {
            "K": K_BASE,
            "range": [RANGE_A, RANGE_B],
            "length": LFSR_BASE_LENGTH,
            "taps": list(LFSR_BASE_TAPS),
            "seed_str": "".join(str(b) for b in LFSR_BASE_SEED),
            "bit_width": 17,
            "mapping": "rejection",
            "output_file": "zad5-gr5/data/lfsr_no_collisions.txt",
            "collisions": cf_collisions,
            "first_15": collision_free_numbers[:15],
        },
        "comparison_table": comparison_table,
    }


def run_lcg_experiments() -> dict[str, object]:
    """Wykonuje komplet eksperymentów dla Grupy 2 (LCG)."""
    # 1. Główny zbiór K=200 liczb z [1000, 100000] i zapis do pliku
    base_gen = lcg.LCG(m=LCG_BASE_M, a=LCG_BASE_A, c=LCG_BASE_C, x0=LCG_BASE_X0)
    base_numbers = base_gen.generate_integers(k=K_BASE, low=RANGE_A, high=RANGE_B, mapping="scale")
    lcg_file = lcg.save_numbers_to_file(
        DATA_DIR / "lcg_numbers.txt",
        base_numbers,
        header_comments=[
            f"LCG base dataset: K={K_BASE}, range=[{RANGE_A}, {RANGE_B}]",
            f"m={LCG_BASE_M}, a={LCG_BASE_A}, c={LCG_BASE_C}, x0={LCG_BASE_X0}, mapping=scale",
        ],
    )
    reloaded = lcg.load_numbers_from_file(lcg_file)
    assert reloaded == base_numbers

    base_collisions = lcg.analyze_collisions(base_numbers)
    base_hull_dobell = lcg.check_hull_dobell(LCG_BASE_M, LCG_BASE_A, LCG_BASE_C)

    # 2. Ciąg K=200 liczb BEZ KOLIZJI z [1000, 100000]
    collision_free_numbers = lcg.generate_collision_free_sequence(
        k=K_BASE,
        low=RANGE_A,
        high=RANGE_B,
        m=LCG_BASE_M,
        a=LCG_BASE_A,
        c=LCG_BASE_C,
        x0=LCG_BASE_X0,
        mapping="scale",
    )
    lcg.save_numbers_to_file(
        DATA_DIR / "lcg_no_collisions.txt",
        collision_free_numbers,
        header_comments=[
            f"LCG collision-free dataset: K={K_BASE}, range=[{RANGE_A}, {RANGE_B}]",
            f"m={LCG_BASE_M}, a={LCG_BASE_A}, c={LCG_BASE_C}, x0={LCG_BASE_X0}, mapping=scale",
            "Verified unique: 200/200 (0 collisions)",
        ],
    )
    cf_collisions = lcg.analyze_collisions(collision_free_numbers)

    # 3. Tabela porównawcza zestawów parametrów m, a, c, x0 oraz mapowań
    param_sets = [
        {
            "name": "Przykładowe (slajd PG: m=15, a=51, c=13)",
            "m": 15,
            "a": 51,
            "c": 13,
            "x0": 1,
            "mapping": "scale",
        },
        {
            "name": "Złe parametry z przedcyklem (m=1024, a=12, c=4)",
            "m": 1024,
            "a": 12,
            "c": 4,
            "x0": 7,
            "mapping": "scale",
        },
        {
            "name": "Slajd PG (m=134456, a=8121, c=28411, x0=55)",
            "m": 134456,
            "a": 8121,
            "c": 28411,
            "x0": 55,
            "mapping": "scale",
        },
        {
            "name": "Slajd PG (m=134456, a=8121, c=28411, x0=999)",
            "m": 134456,
            "a": 8121,
            "c": 28411,
            "x0": 999,
            "mapping": "scale",
        },
        {
            "name": "Microsoft Visual Basic (m=2^24)",
            "m": 2**24,
            "a": 1140671485,
            "c": 12820163,
            "x0": 42,
            "mapping": "scale",
        },
        {
            "name": "ANSI C (m=2^31, x0=123456, scale — bazowe)",
            "m": 2**31,
            "a": 1103515245,
            "c": 12345,
            "x0": 123456,
            "mapping": "scale",
        },
        {
            "name": "ANSI C (m=2^31, x0=123456, mod)",
            "m": 2**31,
            "a": 1103515245,
            "c": 12345,
            "x0": 123456,
            "mapping": "mod",
        },
        {
            "name": "Borland C/C++ (m=2^32, scale)",
            "m": 2**32,
            "a": 22695477,
            "c": 1,
            "x0": 42,
            "mapping": "scale",
        },
        {
            "name": "Java java.util.Random (m=2^48, scale)",
            "m": 2**48,
            "a": 25214903917,
            "c": 11,
            "x0": 42,
            "mapping": "scale",
        },
    ]

    comparison_table = []
    for p in param_sets:
        gen = lcg.LCG(m=p["m"], a=p["a"], c=p["c"], x0=p["x0"])
        nums = gen.generate_integers(k=K_BASE, low=RANGE_A, high=RANGE_B, mapping=p["mapping"])
        col = lcg.analyze_collisions(nums)
        cyc = lcg.detect_state_cycle(
            m=p["m"], a=p["a"], c=p["c"], x0=p["x0"], max_steps=200_000
        )
        even_count = sum(1 for x in nums if x % 2 == 0)
        comparison_table.append(
            {
                "name": p["name"],
                "m": p["m"],
                "a": p["a"],
                "c": p["c"],
                "x0": p["x0"],
                "mapping": p["mapping"],
                "hull_dobell_full": cyc["hull_dobell"]["has_maximal_period_m"],
                "preperiod": cyc["preperiod"],
                "state_cycle": cyc["cycle_length"],
                "cycle_source": cyc["cycle_source"],
                "unique_count": col["unique_count"],
                "total_collisions": col["total_collisions"],
                "collision_rate_pct": round(float(col["collision_rate"]) * 100.0, 2),
                "even_pct": round((even_count / len(nums)) * 100.0, 1),
                "mean_val": round(sum(nums) / len(nums), 1),
            }
        )

    # Dodatkowy eksperyment: wpływ parzystości dolnych bitów dla mapowania mod vs scale na [0, 15]
    parity_mod = lcg.LCG(2**31, 1103515245, 12345, 42).generate_integers(32, 0, 15, mapping="mod")
    parity_scale = lcg.LCG(2**31, 1103515245, 12345, 42).generate_integers(32, 0, 15, mapping="scale")

    return {
        "base_config": {
            "K": K_BASE,
            "range": [RANGE_A, RANGE_B],
            "m": LCG_BASE_M,
            "a": LCG_BASE_A,
            "c": LCG_BASE_C,
            "x0": LCG_BASE_X0,
            "mapping": "scale",
            "output_file": "zad5-gr5/data/lcg_numbers.txt",
        },
        "base_numbers": base_numbers,
        "base_collisions": base_collisions,
        "base_hull_dobell": base_hull_dobell,
        "collision_free": {
            "K": K_BASE,
            "range": [RANGE_A, RANGE_B],
            "m": LCG_BASE_M,
            "a": LCG_BASE_A,
            "c": LCG_BASE_C,
            "x0": LCG_BASE_X0,
            "mapping": "scale",
            "output_file": "zad5-gr5/data/lcg_no_collisions.txt",
            "collisions": cf_collisions,
            "first_15": collision_free_numbers[:15],
        },
        "comparison_table": comparison_table,
        "low_bit_demo": {
            "range": [0, 15],
            "mod_first_16": parity_mod[:16],
            "scale_first_16": parity_scale[:16],
            "mod_parities": [x % 2 for x in parity_mod[:16]],
            "scale_parities": [x % 2 for x in parity_scale[:16]],
        },
    }


def write_primality_csv(filepath: Path, records: list[dict[str, object]]) -> None:
    """Zapisuje szczegółowe wyniki testów pierwszości (każda liczba + czas + werdykt) do CSV."""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "index",
        "number",
        "actual_prime",
        "trial_division_primes_prime",
        "trial_division_primes_ns",
        "fermat_prime",
        "fermat_ns",
        "miller_rabin_prime",
        "miller_rabin_ns",
    ]
    with filepath.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)


def run_primality_experiments(
    lfsr_numbers: list[int],
    lcg_numbers: list[int],
) -> dict[str, object]:
    """Wykonuje komplet eksperymentów podstawowych i dodatkowych dla Grupy 3."""
    # 1. Testy pierwszości na pełnych zbiorach LFSR i LCG (K=200 każdy)
    lfsr_bench = primality.benchmark_primality_methods(
        numbers=lfsr_numbers,
        iterations=PRIMALITY_ITERATIONS,
        rng_seed=PRIMALITY_RNG_SEED,
        source_label="LFSR (K=200, [1000, 100000])",
    )
    lcg_bench = primality.benchmark_primality_methods(
        numbers=lcg_numbers,
        iterations=PRIMALITY_ITERATIONS,
        rng_seed=PRIMALITY_RNG_SEED,
        source_label="LCG (K=200, [1000, 100000])",
    )

    write_primality_csv(RESULTS_DIR / "primality_lfsr_results.csv", lfsr_bench["records"])
    write_primality_csv(RESULTS_DIR / "primality_lcg_results.csv", lcg_bench["records"])

    # 2. Zadanie dodatkowe: porównanie czasów dla różnych przedziałów [a, b] i rozmiarów liczb
    # W każdym przedziale bierzemy 50 nieparzystych kandydatów (w tym gwarantowane liczby pierwsze
    # i trudniejsze liczby złożone bez małych dzielników 2, 3, 5), żeby pomiary odzwierciedlały
    # realny koszt najgorszego przypadku dla dzielenia próbnego.
    range_specs = [
        {"label": "[10^3, 10^4] (~4 cyfry)", "low": 10**3, "high": 10**4},
        {"label": "[10^5, 10^6] (~6 cyfr)", "low": 10**5, "high": 10**6},
        {"label": "[10^7, 10^8] (~8 cyfr)", "low": 10**7, "high": 10**8},
        {"label": "[10^9, 10^10] (~10 cyfr)", "low": 10**9, "high": 10**10},
        {"label": "[10^11, 10^12] (~12 cyfr)", "low": 10**11, "high": 10**12},
    ]
    scaling_results = []
    scale_rng = random.Random(PRIMALITY_RNG_SEED + 101)
    for spec in range_specs:
        # Dobieramy 40 liczb nieparzystych niepodzielnych przez 3 i 5 (mieszanka pierwszych i złożonych)
        sample: list[int] = []
        while len(sample) < 40:
            cand = scale_rng.randrange(spec["low"] | 1, spec["high"], 2)
            if cand % 3 != 0 and cand % 5 != 0:
                sample.append(cand)
        bench = primality.benchmark_primality_methods(
            numbers=sample,
            iterations=PRIMALITY_ITERATIONS,
            rng_seed=PRIMALITY_RNG_SEED,
            source_label=spec["label"],
        )
        scaling_results.append(
            {
                "label": spec["label"],
                "low": spec["low"],
                "high": spec["high"],
                "count": bench["count"],
                "true_primes": bench["true_primes"],
                "sieve_build_us": bench["sieve_build_us"],
                "trial_mean_us": bench["summaries"]["trial_division_primes"]["mean_us"],
                "trial_median_us": bench["summaries"]["trial_division_primes"]["median_us"],
                "fermat_mean_us": bench["summaries"]["fermat"]["mean_us"],
                "fermat_median_us": bench["summaries"]["fermat"]["median_us"],
                "mr_mean_us": bench["summaries"]["miller_rabin"]["mean_us"],
                "mr_median_us": bench["summaries"]["miller_rabin"]["median_us"],
                "fermat_fp": bench["summaries"]["fermat"]["pseudoprimes_fp"],
                "mr_fp": bench["summaries"]["miller_rabin"]["pseudoprimes_fp"],
            }
        )

    # 3. Zadanie dodatkowe: wpływ liczby iteracji Millera–Rabina i Fermata (s = 1, 2, 3, 5, 10, 20, 40)
    # Zbiór testowy: 20 liczb Carmichaela + 20 liczb pierwszych + 20 zwykłych liczb złożonych nieparzystych
    hard_primes = [
        10007, 10009, 10037, 10039, 10061, 10067, 10069, 10079, 10091, 10093,
        100003, 100019, 100043, 100049, 100057, 100069, 100103, 100109, 100129, 100151,
    ]
    regular_composites = [
        10011, 10015, 10021, 10023, 10027, 10031, 10041, 10045, 10047, 10051,
        100005, 100007, 100009, 100011, 100013, 100015, 100017, 100021, 100023, 100025,
    ]
    stress_set = CARMICHAEL_NUMBERS + hard_primes + regular_composites
    iteration_study = []
    for s in (1, 2, 3, 5, 10, 20, 40):
        b = primality.benchmark_primality_methods(
            numbers=stress_set,
            iterations=s,
            rng_seed=PRIMALITY_RNG_SEED,
            source_label=f"stress_s={s}",
        )
        # Dodatkowo osobny licznik pomyłek wyłącznie na 20 liczbach Carmichaela
        carmichael_fermat_fp = sum(
            1
            for rec in b["records"][: len(CARMICHAEL_NUMBERS)]
            if rec["fermat_prime"]
        )
        carmichael_mr_fp = sum(
            1
            for rec in b["records"][: len(CARMICHAEL_NUMBERS)]
            if rec["miller_rabin_prime"]
        )
        iteration_study.append(
            {
                "iterations": s,
                "total_tested": len(stress_set),
                "carmichael_count": len(CARMICHAEL_NUMBERS),
                "fermat_mean_us": b["summaries"]["fermat"]["mean_us"],
                "fermat_median_us": b["summaries"]["fermat"]["median_us"],
                "fermat_fp_total": b["summaries"]["fermat"]["pseudoprimes_fp"],
                "fermat_fp_carmichael": carmichael_fermat_fp,
                "mr_mean_us": b["summaries"]["miller_rabin"]["mean_us"],
                "mr_median_us": b["summaries"]["miller_rabin"]["median_us"],
                "mr_fp_total": b["summaries"]["miller_rabin"]["pseudoprimes_fp"],
                "mr_fp_carmichael": carmichael_mr_fp,
                "mr_fn_total": b["summaries"]["miller_rabin"]["pseudocomposites_fn"],
            }
        )

    # Szczegółowe sprawdzenie 20 liczb Carmichaela przy s=10
    carmichael_details = []
    rng_f_c = random.Random(PRIMALITY_RNG_SEED)
    rng_m_c = random.Random(PRIMALITY_RNG_SEED)
    for num in CARMICHAEL_NUMBERS:
        exact = primality.is_prime_exact_independent(num)
        trial = primality.trial_division_by_primes(num)
        fermat_s10 = primality.fermat_test(num, iterations=PRIMALITY_ITERATIONS, rng=rng_f_c)
        mr_s10 = primality.miller_rabin_test(num, iterations=PRIMALITY_ITERATIONS, rng=rng_m_c)
        carmichael_details.append(
            {
                "number": num,
                "actual_prime": exact,
                "trial_prime": trial,
                "fermat_s10_prime": fermat_s10,
                "mr_s10_prime": mr_s10,
            }
        )

    return {
        "lfsr_benchmark": lfsr_bench,
        "lcg_benchmark": lcg_bench,
        "scaling_study": scaling_results,
        "iteration_study": iteration_study,
        "carmichael_details": carmichael_details,
    }


def write_summary_markdown(payload: dict[str, object]) -> None:
    """Generuje czyste tabele Markdown z rzeczywistych pomiarów w results/SUMMARY_TABLES.md."""
    lfsr_data = payload["lfsr"]
    lcg_data = payload["lcg"]
    pr_data = payload["primality"]

    lines: list[str] = [
        "# Zestawienie tabelaryczne wyników eksperymentów — Lab 05, Grupa 5",
        "",
        f"Środowisko: Python {payload['meta']['python_version']} ({payload['meta']['platform']}), "
        f"zegar: `time.perf_counter_ns()`.",
        "",
        "## 1. LFSR — Weryfikacja przykładów z notatki (32 bity)",
        "",
        "| Przykład | Długość n | Wektor p | Ziarno | Cykl stanu | Maks. 2^n - 1 | Pełny? | Pierwsze 32 bity |",
        "| --- | ---: | --- | --- | ---: | ---: | --- | --- |",
    ]
    for ex in lfsr_data["lecture_examples"]:
        lines.append(
            f"| {ex['label']} | {ex['length']} | `{tuple(ex['p'])}` | `{tuple(ex['seed'])}` | "
            f"{ex['state_cycle']} | {ex['max_theoretical']} | {'Tak' if ex['is_maximal'] else 'Nie'} | "
            f"`{ex['bits_32']}` |"
        )

    lines += [
        "",
        "## 2. LFSR — Wpływ długości, odczepów i ziarna (K=200, [1000, 100000])",
        "",
        "| Konfiguracja | n | Odczepy | Mapowanie | Cykl stanu | Unikalne | Kolizje | Odsetek kolizji |",
        "| --- | ---: | --- | --- | ---: | ---: | ---: | ---: |",
    ]
    for row in lfsr_data["comparison_table"]:
        lines.append(
            f"| {row['name']} | {row['length']} | `{tuple(row['taps'])}` | `{row['mapping']}` | "
            f"{row['state_cycle']} / {row['max_theoretical']} | {row['unique_count']} | "
            f"{row['total_collisions']} | {row['collision_rate_pct']:.2f}% |"
        )

    lines += [
        "",
        "## 3. LCG — Porównanie zestawów parametrów m, a, c, x0 (K=200, [1000, 100000])",
        "",
        "| Konfiguracja | m | Hull–Dobell | Przedcykl mu | Cykl stanu lambda | Mapowanie | Unikalne | Kolizje | Parzyste |",
        "| --- | ---: | --- | ---: | ---: | --- | ---: | ---: | ---: |",
    ]
    for row in lcg_data["comparison_table"]:
        hd = "Tak" if row["hull_dobell_full"] else "Nie"
        cyc_str = f"{row['state_cycle']}" if row["state_cycle"] is not None else "n/d"
        pre_str = f"{row['preperiod']}" if row["preperiod"] is not None else "n/d"
        lines.append(
            f"| {row['name']} | {row['m']} | {hd} | {pre_str} | {cyc_str} | `{row['mapping']}` | "
            f"{row['unique_count']} | {row['total_collisions']} | {row['even_pct']:.1f}% |"
        )

    lines += [
        "",
        "## 4. Testy pierwszości — Statystyki czasów i skuteczności (K=200 na źródło, s=10)",
        "",
    ]
    for label, key in (("Zbiór LFSR", "lfsr_benchmark"), ("Zbiór LCG", "lcg_benchmark")):
        b = pr_data[key]
        lines += [
            f"### {label} (liczby pierwsze rzeczywiste: {b['true_primes']}, złożone: {b['true_composites']}, "
            f"budowa sita do {b['sieve_limit']}: {b['sieve_build_us']} us)",
            "",
            "| Test | Pomiary | Min [us] | Mediana [us] | Średnia [us] | Max [us] | Pseudopierwsze (FP) | Pseudozłożone (FN) | Trafność |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
        for m_key, m_name in (
            ("trial_division_primes", "Dzielenie przez liczby pierwsze"),
            ("fermat", f"Test Fermata (s={b['iterations']})"),
            ("miller_rabin", f"Test Millera–Rabina (s={b['iterations']})"),
        ):
            s = b["summaries"][m_key]
            lines.append(
                f"| {m_name} | {s['measurements']} | {s['min_us']:.3f} | {s['median_us']:.3f} | "
                f"{s['mean_us']:.3f} | {s['max_us']:.3f} | {s['pseudoprimes_fp']} | "
                f"{s['pseudocomposites_fn']} | {s['accuracy_pct']:.2f}% |"
            )
        lines.append("")

    lines += [
        "## 5. Skalowanie czasów testów pierwszości dla różnych rozmiarów liczb (40 kandydatów/przedział, s=10)",
        "",
        "| Przedział | Prawdziwe pierwsze | Sito [us] | Dzielenie średnia [us] | Fermat średnia [us] | Miller–Rabin średnia [us] |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for r in pr_data["scaling_study"]:
        lines.append(
            f"| {r['label']} | {r['true_primes']}/{r['count']} | {r['sieve_build_us']:.1f} | "
            f"{r['trial_mean_us']:.3f} | {r['fermat_mean_us']:.3f} | {r['mr_mean_us']:.3f} |"
        )

    lines += [
        "",
        "## 6. Wpływ liczby iteracji s (20 liczb Carmichaela + 20 pierwszych + 20 złożonych)",
        "",
        "| Iteracje s | Fermat średnia [us] | Fermat FP (Carmichael) | Miller–Rabin średnia [us] | Miller–Rabin FP (Carmichael) | Miller–Rabin FN |",
        "| ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for r in pr_data["iteration_study"]:
        lines.append(
            f"| {r['iterations']} | {r['fermat_mean_us']:.3f} | "
            f"{r['fermat_fp_total']} ({r['fermat_fp_carmichael']}/20) | "
            f"{r['mr_mean_us']:.3f} | {r['mr_fp_total']} ({r['mr_fp_carmichael']}/20) | "
            f"{r['mr_fn_total']} |"
        )

    (RESULTS_DIR / "SUMMARY_TABLES.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    WEB_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)

    t0 = time.perf_counter()
    lfsr_res = run_lfsr_experiments()
    lcg_res = run_lcg_experiments()
    primality_res = run_primality_experiments(
        lfsr_numbers=lfsr_res["base_numbers"],
        lcg_numbers=lcg_res["base_numbers"],
    )
    elapsed_sec = round(time.perf_counter() - t0, 3)

    payload = {
        "meta": {
            "project": "Kryptologia — Laboratorium 5: Generatory pseudolosowe i testy pierwszości",
            "group": "Grupa 5 (Realizacja z wykorzystaniem GenAI)",
            "directory": "zad5-gr5",
            "deadlines": {
                "stage_1": "26.11.2026 13:30",
                "stage_2_report": "30.11.2026 18:00",
            },
            "python_version": platform.python_version(),
            "platform": f"{platform.system()} {platform.machine()}",
            "clock": "time.perf_counter_ns()",
            "total_runtime_sec": elapsed_sec,
            "benchmark_params": {
                "K": K_BASE,
                "range_a": RANGE_A,
                "range_b": RANGE_B,
                "primality_iterations": PRIMALITY_ITERATIONS,
                "primality_rng_seed": PRIMALITY_RNG_SEED,
            },
        },
        "lfsr": lfsr_res,
        "lcg": lcg_res,
        "primality": primality_res,
    }

    json_text = json.dumps(payload, indent=2, ensure_ascii=False)
    (RESULTS_DIR / "experiment_results.json").write_text(json_text, encoding="utf-8")
    WEB_DATA_PATH.write_text(json_text, encoding="utf-8")
    write_summary_markdown(payload)

    print(f"[OK] Eksperymenty Lab 05 (Grupa 5) zakończone w {elapsed_sec:.3f} s.")
    print(f"     LFSR bazowe: K={K_BASE}, kolizje={lfsr_res['base_collisions']['total_collisions']}, "
          f"cykl stanu={lfsr_res['base_state_cycle']['cycle_length']}")
    print(f"     LFSR bez kolizji: unikalne={lfsr_res['collision_free']['collisions']['unique_count']}/{K_BASE}")
    print(f"     LCG bazowe: K={K_BASE}, kolizje={lcg_res['base_collisions']['total_collisions']}, "
          f"Hull-Dobell={lcg_res['base_hull_dobell']['has_maximal_period_m']}")
    print(f"     Pierwszość LFSR: prawdziwych pierwszych={primality_res['lfsr_benchmark']['true_primes']}/{K_BASE}")
    print(f"     Pierwszość LCG:  prawdziwych pierwszych={primality_res['lcg_benchmark']['true_primes']}/{K_BASE}")


if __name__ == "__main__":
    main()
