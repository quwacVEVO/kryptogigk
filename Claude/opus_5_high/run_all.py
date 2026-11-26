"""Jedno wejście odtwarzające cały eksperyment: testy + trzy części zadania.

Uruchomienie:  python3 run_all.py

Kolejność jest istotna: testy pierwszości czytają pliki z liczbami wytworzone
przez generatory, więc LFSR i LCG muszą zadziałać przed nimi.

Wytwarza dodatkowo:
  results/summary.md     - skrót wszystkich najważniejszych liczb z przebiegu,
  results/benchmark.json - te same liczby w formie maszynowej, do porównania
                           innego modelu GenAI na tych samych wejściach.
"""

import hashlib
import json
import os
import platform
import sys
import time
import unittest

import demo_errors
import exp_lcg
import exp_lfsr
import exp_primality
import params
from common import time_stats, write_text


def run_tests():
    """Uruchamia pełny zestaw testów jednostkowych i zwraca podsumowanie."""
    loader = unittest.TestLoader()
    suite = loader.discover(os.path.dirname(os.path.abspath(__file__)), pattern="test_*.py")
    runner = unittest.TextTestRunner(verbosity=1, stream=sys.stdout)
    result = runner.run(suite)
    return {
        "testow": result.testsRun,
        "bledow": len(result.errors),
        "niezaliczonych": len(result.failures),
        "pominietych": len(result.skipped),
        "wynik": "OK" if result.wasSuccessful() else "NIEPOWODZENIE",
    }


def sha256_of(path):
    """Suma kontrolna pliku - pozwala sprawdzić, czy inny przebieg dał te same dane."""
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        digest.update(handle.read())
    return digest.hexdigest()


def main():
    started = time.perf_counter()
    print("=" * 78)
    print("lab05 / grupa 5 (GenAI) - pełny przebieg")
    print("=" * 78)

    print("\n[1/5] testy poprawności")
    tests = run_tests()

    print("\n[2/5] LFSR (zakres grupy 1)")
    lfsr = exp_lfsr.run()
    print("  okres stanu {} (ogon {}), okres wartości {}, kolizji {} / K={}".format(
        lfsr["main"]["state_period"], lfsr["main"]["tail"], lfsr["main"]["value_period"],
        lfsr["main"]["collisions"]["collisions"], params.K))

    print("\n[3/5] LCG (zakres grupy 2)")
    lcg = exp_lcg.run()
    print("  okres stanu {} (ogon {}), okres wartości {}, kolizji {} / K={}".format(
        lcg["main"]["state_period"], lcg["main"]["tail"], lcg["main"]["value_period"],
        lcg["main"]["collisions"]["collisions"], params.K))

    print("\n[4/5] testy pierwszości (zakres grupy 3)")
    primality = exp_primality.run()
    for source, times in primality["times"].items():
        for name in exp_primality.TESTS:
            stats = time_stats(times[name])
            print("  {:5s} {:13s} n={} mediana={:.0f} ns średnia={:.0f} ns".format(
                source, name, stats["n"], stats["median_ns"], stats["mean_ns"]))

    print("\n[5/5] kontrola błędów (wymagania dodatkowe)")
    errors = demo_errors.run()
    print("  przypadków błędnych: {}, nieodrzuconych: {}".format(
        errors["cases"], errors["not_caught"]))

    elapsed = time.perf_counter() - started

    # ---------------------------------------------------------------- benchmark maszynowy
    number_files = {
        "lfsr_main": lfsr["main"]["path"],
        "lfsr_unique": lfsr["unique_filtered"]["path"],
        "lfsr_raw_unique": lfsr["unique_raw"]["path"],
        "lcg_main": lcg["main"]["path"],
        "lcg_unique": lcg["unique_filtered"]["path"],
        "lcg_raw_unique": lcg["unique_raw"]["path"],
    }
    benchmark = {
        "opis": "lab05 grupa 5 (GenAI) - wyniki jednego przebiegu, format do porównania modeli",
        "model": {
            "nazwa": "Claude Opus 5 (claude-opus-5), tryb Claude Code, effort=high",
            "uwaga": "wersja modelu podana przez środowisko uruchomieniowe; nie weryfikowana niezależnie",
        },
        "srodowisko": {
            "python": sys.version.split()[0],
            "implementacja": platform.python_implementation(),
            "system": "{} {}".format(platform.system(), platform.release()),
            "maszyna": platform.machine(),
            "procesor": exp_primality.cpu_model(),
            "czas_przebiegu_s": round(elapsed, 3),
        },
        "parametry": {
            "K": params.K, "przedzial": [params.LOW, params.HIGH],
            "lfsr": {"n": params.LFSR_N, "odczepy": list(params.LFSR_TAP_INDICES),
                     "ziarno": params.LFSR_SEED, "mapowanie": params.LFSR_MAPPING},
            "lcg": {"m": params.LCG_M, "a": params.LCG_A, "c": params.LCG_C,
                    "x0": params.LCG_X0, "mapowanie": params.LCG_MAPPING},
            "testy": {"fermat_iteracje": params.FERMAT_ROUNDS,
                      "mr_iteracje": params.MR_ROUNDS,
                      "ziarno_losowania": params.RNG_SEED},
        },
        "testy_jednostkowe": tests,
        "kontrola_bledow": errors,
        "lfsr": {
            "okres_stanu": lfsr["main"]["state_period"],
            "ogon": lfsr["main"]["tail"],
            "okres_wartosci": lfsr["main"]["value_period"],
            "kolizje": lfsr["main"]["collisions"]["collisions"],
            "roznych_wartosci": lfsr["main"]["collisions"]["unique"],
            "ziarno_ciagu_bez_kolizji": lfsr["unique_raw"]["seed"],
        },
        "lcg": {
            "okres_stanu": lcg["main"]["state_period"],
            "ogon": lcg["main"]["tail"],
            "okres_wartosci": lcg["main"]["value_period"],
            "kolizje": lcg["main"]["collisions"]["collisions"],
            "roznych_wartosci": lcg["main"]["collisions"]["unique"],
            "hull_dobell_spelnione": lcg["main"]["hull_dobell"][0],
        },
        "pierwszosc": {
            "czasy_ns": {
                source: {name: time_stats(times[name]) for name in exp_primality.TESTS}
                for source, times in primality["times"].items()
            },
            "trafnosc": {
                source: {
                    name: {
                        "unikalnych": data["summary"][name]["unique"],
                        "pierwszych": data["summary"][name]["primes"],
                        "zlozonych": data["summary"][name]["composites"],
                        "pseudopierwszych": len(data["summary"][name]["pseudoprime"]),
                        "pseudozlozonych": len(data["summary"][name]["pseudocomposite"]),
                    }
                    for name in ("Fermat", "Miller-Rabin")
                }
                for source, data in primality["accuracy"].items()
            },
            "mr_wplyw_iteracji": [
                {"s": row[0], "srednia_ns": float(row[4]), "pseudopierwszych": row[6],
                 "pseudozlozonych": row[7]}
                for row in primality["mr_sweep"]
            ],
            "fermat_wplyw_iteracji": [
                {"s": row[0], "srednia_ns": float(row[4]), "pseudopierwszych": row[6],
                 "pseudozlozonych": row[7]}
                for row in primality["fermat_sweep"]
            ],
        },
        "sumy_kontrolne_sha256": {
            name: sha256_of(path) for name, path in number_files.items() if path
        },
    }
    benchmark_path = os.path.join(params.RESULTS_DIR, "benchmark.json")
    write_text(benchmark_path, json.dumps(benchmark, indent=2, ensure_ascii=False))

    # ---------------------------------------------------------------- skrót dla człowieka
    summary = ["# Skrót przebiegu (plik generowany przez run_all.py)", ""]
    summary.append("* data uruchomienia (czas lokalny): {}".format(
        time.strftime("%Y-%m-%d %H:%M:%S")))
    summary.append("* czas całego przebiegu: {:.1f} s".format(elapsed))
    summary.append("* testy jednostkowe: {} testów, wynik {} (błędów {}, niezaliczonych {})".format(
        tests["testow"], tests["wynik"], tests["bledow"], tests["niezaliczonych"]))
    summary.append("* kontrola błędów: {} wymuszonych przypadków, nieodrzuconych {}".format(
        errors["cases"], errors["not_caught"]))
    summary.append("")
    summary.append("## LFSR")
    summary.append("* parametry: {}".format(lfsr["main"]["params"]))
    summary.append("* okres stanu {} (ogon {}), okres ciągu wartości {}".format(
        lfsr["main"]["state_period"], lfsr["main"]["tail"], lfsr["main"]["value_period"]))
    summary.append("* kolizje w K={}: {} (różnych {})".format(
        params.K, lfsr["main"]["collisions"]["collisions"], lfsr["main"]["collisions"]["unique"]))
    summary.append("")
    summary.append("## LCG")
    summary.append("* parametry: {}".format(lcg["main"]["params"]))
    summary.append("* okres stanu {} (ogon {}), okres ciągu wartości {}".format(
        lcg["main"]["state_period"], lcg["main"]["tail"], lcg["main"]["value_period"]))
    summary.append("* kolizje w K={}: {} (różnych {})".format(
        params.K, lcg["main"]["collisions"]["collisions"], lcg["main"]["collisions"]["unique"]))
    summary.append("")
    summary.append("## Testy pierwszości (scenariusz główny)")
    for source, times in primality["times"].items():
        for name in exp_primality.TESTS:
            stats = time_stats(times[name])
            summary.append("* {} / {}: pomiarów {}, min {} ns, mediana {:.0f} ns, "
                           "średnia {:.0f} ns, max {} ns".format(
                               source, name, stats["n"], stats["min_ns"], stats["median_ns"],
                               stats["mean_ns"], stats["max_ns"]))
    for source, data in primality["accuracy"].items():
        for name in ("Fermat", "Miller-Rabin"):
            item = data["summary"][name]
            summary.append("* {} / {}: pseudopierwszych {}, pseudozłożonych {} "
                           "(unikalnych {}, pierwszych {})".format(
                               source, name, len(item["pseudoprime"]),
                               len(item["pseudocomposite"]), item["unique"], item["primes"]))
    summary.append("")
    summary.append("## Pliki")
    for name, path in sorted(number_files.items()):
        if path:
            summary.append("* `{}` - {}".format(path, name))
    for path in (lfsr["analysis_path"], lcg["analysis_path"], primality["analysis_path"],
                 errors["path"], benchmark_path,
                 os.path.join(params.RESULTS_DIR, "environment.txt")):
        summary.append("* `{}`".format(path))
    summary_path = write_text(os.path.join(params.RESULTS_DIR, "summary.md"), "\n".join(summary))

    print("\n" + "=" * 78)
    print("gotowe w {:.1f} s; skrót: {}; benchmark: {}".format(elapsed, summary_path, benchmark_path))
    print("=" * 78)
    return 0 if tests["wynik"] == "OK" else 1


if __name__ == "__main__":
    raise SystemExit(main())
