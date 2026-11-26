"""Eksperymenty dla testów pierwszości (zakres grupy 3).

Uruchomienie:  python3 exp_primality.py
Wyniki:        results/primality_calls_*.csv, results/primality_analysis.md

Zasady pomiaru przyjęte w tym przebiegu (ważne dla porównywalności):

1. Dane wejściowe są WCZYTYWANE Z PLIKÓW wygenerowanych przez exp_lfsr.py i exp_lcg.py,
   więc testowane są dokładnie te liczby, które oddają grupy 1 i 2.
2. Czas wczytania pliku NIE jest doliczany do czasu testu - mierzone jest wyłącznie
   wywołanie funkcji testującej (`common.measure_ns`, zegar `time.perf_counter_ns`).
3. Statystyki czasu liczone są dla KAŻDEJ POZYCJI pliku (K pomiarów na test), również
   dla liczb powtórzonych - taki jest naturalny koszt przetworzenia pliku wyników.
4. Trafność decyzji liczona jest osobnym przebiegiem po ZBIORZE UNIKALNYCH liczb, żeby
   jedna liczba nie była liczona wielokrotnie do statystyki błędów.
5. Lista liczb pierwszych dla testu dzielenia jest budowana PRZED pomiarami
   (`prepare_primes`), inaczej pierwsze wywołanie zawierałoby koszt sita.
6. Każdy test w każdym scenariuszu dostaje świeży `random.Random(params.RNG_SEED)`,
   więc losowane podstawy są identyczne przy każdym uruchomieniu.
7. Podstawą odniesienia ("rzeczywisty status pierwszości") jest wyłącznie DOKŁADNY
   test dzielenia przez liczby pierwsze do floor(sqrt(n)).
"""

import os
import platform
import random
import sys
import time
from math import isqrt

import params
from common import markdown_table, measure_ns, read_numbers, time_stats, write_csv, write_text
from lcg import LCG
from lfsr import LFSR
from primality import (KNOWN_CARMICHAEL, fermat_is_probably_prime,
                       miller_rabin_is_probably_prime, prepare_primes, trial_division_is_prime)

TESTS = ("dzielenie", "Fermat", "Miller-Rabin")


def make_test_callables(fermat_rounds=None, mr_rounds=None):
    """Słownik nazwa_testu -> funkcja jednoargumentowa, każda z własnym generatorem podstaw."""
    fermat_rounds = params.FERMAT_ROUNDS if fermat_rounds is None else fermat_rounds
    mr_rounds = params.MR_ROUNDS if mr_rounds is None else mr_rounds
    fermat_rng = random.Random(params.RNG_SEED)
    mr_rng = random.Random(params.RNG_SEED)
    return {
        "dzielenie": lambda n: trial_division_is_prime(n),
        "Fermat": lambda n: fermat_is_probably_prime(n, fermat_rounds, fermat_rng),
        "Miller-Rabin": lambda n: miller_rabin_is_probably_prime(n, mr_rounds, mr_rng),
    }


def warmup(numbers, fermat_rounds=None, mr_rounds=None):
    """Przebieg rozgrzewkowy: te same testy bez pomiaru czasu.

    Pierwsze wywołania w świeżym procesie są wolniejsze (import, pamięci podręczne
    procesora, alokacje), co przy bardzo krótkich wywołaniach widać w statystykach.
    Rozgrzewka używa OSOBNEGO generatora podstaw, więc nie zmienia podstaw losowanych
    w przebiegu mierzonym.
    """
    callables = make_test_callables(fermat_rounds, mr_rounds)
    for number in numbers:
        for name in TESTS:
            callables[name](number)


def run_battery(numbers, fermat_rounds=None, mr_rounds=None):
    """Uruchamia wszystkie trzy testy na każdej pozycji listy, zwraca wiersze i czasy."""
    warmup(numbers, fermat_rounds, mr_rounds)
    callables = make_test_callables(fermat_rounds, mr_rounds)
    rows = []
    times = {name: [] for name in TESTS}
    decisions = {name: [] for name in TESTS}
    for position, number in enumerate(numbers):
        for name in TESTS:
            result, elapsed = measure_ns(callables[name], number)
            rows.append([position, number, name, int(result), elapsed])
            times[name].append(elapsed)
            decisions[name].append(result)
    return rows, times, decisions


def accuracy_over_unique(numbers, fermat_rounds=None, mr_rounds=None):
    """Trafność decyzji na zbiorze unikalnych liczb, względem dokładnego dzielenia.

    pseudopierwsza   - test probabilistyczny mówi "pierwsza", a liczba jest złożona,
    pseudozłożona    - test mówi "złożona", a liczba jest pierwsza (dla poprawnie
                       zaimplementowanych testów Fermata i Millera-Rabina niemożliwe).
    """
    unique = sorted(set(numbers))
    callables = make_test_callables(fermat_rounds, mr_rounds)
    truth = {n: trial_division_is_prime(n) for n in unique}
    summary = {}
    for name in ("Fermat", "Miller-Rabin"):
        false_primes, false_composites = [], []
        for n in unique:
            decision = callables[name](n)
            if decision and not truth[n]:
                false_primes.append(n)
            elif not decision and truth[n]:
                false_composites.append(n)
        summary[name] = {
            "unique": len(unique),
            "primes": sum(1 for n in unique if truth[n]),
            "composites": sum(1 for n in unique if not truth[n]),
            "pseudoprime": false_primes,
            "pseudocomposite": false_composites,
        }
    return unique, truth, summary


def fmt(value, digits=1):
    if value is None:
        return "-"
    return "{:.{}f}".format(value, digits)


def stats_table(times_by_source):
    """Tabela min/max/średnia/mediana osobno dla każdego testu i źródła liczb."""
    rows = []
    for source, times in times_by_source.items():
        for name in TESTS:
            stats = time_stats(times[name])
            rows.append([source, name, stats["n"], stats["min_ns"], stats["max_ns"],
                         fmt(stats["mean_ns"]), fmt(stats["median_ns"])])
    return rows


def group_stats_table(rows_by_source, truth_by_source):
    """Czasy rozbite na grupy liczb - rozkład czasów jest dwumodalny.

    Dla testów probabilistycznych: liczby parzyste (oraz n < 2, 2, 3) kończą się
    na sprawdzeniu warunków brzegowych, a liczby nieparzyste >= 5 wymagają s
    potęgowań modulo. Dla dzielenia próbnego: liczba złożona zwykle ma mały
    dzielnik i kończy się po kilku dzieleniach, a liczba pierwsza wymaga przejścia
    po wszystkich liczbach pierwszych do floor(sqrt(n)).
    """
    out = []
    for source, rows in rows_by_source.items():
        truth = truth_by_source[source]
        groups = {}
        for _, number, test, _, elapsed in rows:
            if test == "dzielenie":
                label = "pierwsza" if truth[number] else "złożona"
            else:
                label = ("wyjście brzegowe (n < 2, 2, 3 lub parzysta)"
                         if number < 2 or number in (2, 3) or number % 2 == 0
                         else "pełny test (nieparzysta >= 5)")
            groups.setdefault((test, label), []).append(elapsed)
        for (test, label), samples in sorted(groups.items()):
            stats = time_stats(samples)
            out.append([source, test, label, stats["n"], stats["min_ns"], stats["max_ns"],
                        fmt(stats["mean_ns"]), fmt(stats["median_ns"])])
    return out


def edge_case_table():
    """Przypadki brzegowe i liczby trudne dla testu Fermata."""
    cases = [-7, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 25, 97, 341, 561, 1105, 1729, 2465,
             7919, 104729, 1000003, 1000001]
    rng_f = random.Random(params.RNG_SEED)
    rng_m = random.Random(params.RNG_SEED)
    rows = []
    for n in cases:
        exact = trial_division_is_prime(n)
        fermat = fermat_is_probably_prime(n, params.FERMAT_ROUNDS, rng_f)
        miller = miller_rabin_is_probably_prime(n, params.MR_ROUNDS, rng_m)
        note = []
        if n in KNOWN_CARMICHAEL:
            note.append("liczba Carmichaela")
        if n == 341:
            note.append("najmniejsza pseudopierwsza Fermata dla podstawy 2")
        if n < 2:
            note.append("poza zakresem pierwszości")
        rows.append([n, "pierwsza" if exact else "złożona",
                     "pierwsza" if fermat else "złożona",
                     "pierwsza" if miller else "złożona",
                     "tak" if fermat == exact else "BŁĄD",
                     "tak" if miller == exact else "BŁĄD",
                     ", ".join(note)])
    return rows


def liars_table():
    """Dokładna (wyczerpująca) liczba podstaw mylących oba testy dla liczb Carmichaela.

    Dla każdej podstawy t z {2, ..., n-2} sprawdzamy jednoiteracyjną wersję testu.
    To nie jest pomiar losowy, tylko przeliczenie wszystkich możliwości.
    """
    from primality import decompose, pow_mod

    rows = []
    for n in KNOWN_CARMICHAEL:
        bases = range(2, n - 1)
        total = len(bases)
        fermat_liars = sum(1 for t in bases if pow_mod(t, n - 1, n) == 1)

        u, r = decompose(n)
        mr_liars = 0
        for t in bases:
            value = pow_mod(t, r, n)
            if value == 1:
                mr_liars += 1
                continue
            squarings = 0
            passed = True
            while value != n - 1:
                value = (value * value) % n
                squarings += 1
                if value == 1 or squarings == u:
                    passed = False
                    break
            if passed:
                mr_liars += 1
        rows.append([
            n, total, fermat_liars, fmt(100 * fermat_liars / total, 2),
            mr_liars, fmt(100 * mr_liars / total, 2),
            fmt(100 * (fermat_liars / total) ** params.FERMAT_ROUNDS, 3),
        ])
    return rows


def range_tables():
    """Czasy testów dla różnych przedziałów i rozmiarów liczb (wymaganie dodatkowe)."""
    rows = []
    details = []
    for label, low, high in params.RANGE_SCENARIOS:
        span = high - low + 1
        lfsr = LFSR.from_tap_indices(params.LFSR_N, params.LFSR_TAP_INDICES, params.LFSR_SEED)
        lcg = LCG(m=params.LCG_BIG_M, a=params.LCG_BIG_A, c=params.LCG_BIG_C, x0=params.LCG_BIG_X0)
        numbers = (lfsr.numbers(params.RANGE_K, low, high, mode=params.LFSR_MAPPING)
                   + lcg.numbers(params.RANGE_K, low, high, mode=params.LCG_MAPPING))
        prepare_primes(isqrt(max(numbers)))
        _, times, decisions = run_battery(numbers)
        primes_found = sum(decisions["dzielenie"])
        for name in TESTS:
            stats = time_stats(times[name])
            rows.append([label, span, name, stats["n"], stats["min_ns"], stats["max_ns"],
                         fmt(stats["mean_ns"]), fmt(stats["median_ns"])])
        details.append([label, len(numbers), primes_found,
                        fmt(100 * primes_found / len(numbers), 1)])
    return rows, details


def mr_sweep(numbers):
    """Wpływ liczby iteracji Millera-Rabina na czas i liczbę błędnych decyzji."""
    unique = sorted(set(numbers))
    truth = {n: trial_division_is_prime(n) for n in unique}
    rows = []
    for rounds in params.MR_ROUNDS_SWEEP:
        warm_rng = random.Random(params.RNG_SEED + 1)
        for n in unique:
            miller_rabin_is_probably_prime(n, rounds, warm_rng)
        rng = random.Random(params.RNG_SEED)
        times, pseudoprimes, pseudocomposites = [], [], []
        for n in unique:
            decision, elapsed = measure_ns(miller_rabin_is_probably_prime, n, rounds, rng)
            times.append(elapsed)
            if decision and not truth[n]:
                pseudoprimes.append(n)
            elif not decision and truth[n]:
                pseudocomposites.append(n)
        stats = time_stats(times)
        rows.append([rounds, stats["n"], stats["min_ns"], stats["max_ns"],
                     fmt(stats["mean_ns"]), fmt(stats["median_ns"]),
                     len(pseudoprimes), len(pseudocomposites),
                     ", ".join(map(str, pseudoprimes)) or "brak"])
    return rows


def fermat_sweep(numbers):
    """Dla porównania: wpływ liczby iteracji testu Fermata na te same dane."""
    unique = sorted(set(numbers))
    truth = {n: trial_division_is_prime(n) for n in unique}
    rows = []
    for rounds in params.MR_ROUNDS_SWEEP:
        warm_rng = random.Random(params.RNG_SEED + 1)
        for n in unique:
            fermat_is_probably_prime(n, rounds, warm_rng)
        rng = random.Random(params.RNG_SEED)
        times, pseudoprimes, pseudocomposites = [], [], []
        for n in unique:
            decision, elapsed = measure_ns(fermat_is_probably_prime, n, rounds, rng)
            times.append(elapsed)
            if decision and not truth[n]:
                pseudoprimes.append(n)
            elif not decision and truth[n]:
                pseudocomposites.append(n)
        stats = time_stats(times)
        rows.append([rounds, stats["n"], stats["min_ns"], stats["max_ns"],
                     fmt(stats["mean_ns"]), fmt(stats["median_ns"]),
                     len(pseudoprimes), len(pseudocomposites),
                     ", ".join(map(str, pseudoprimes)) or "brak"])
    return rows


def cpu_model():
    """Model procesora z /proc/cpuinfo (platform.processor() na Linuksie bywa puste)."""
    try:
        with open("/proc/cpuinfo", encoding="utf-8") as handle:
            for line in handle:
                if line.startswith("model name"):
                    return line.split(":", 1)[1].strip()
    except OSError:
        pass
    return platform.processor() or "nieustalony"


def environment_lines():
    clock = time.get_clock_info("perf_counter")
    return [
        "Python: {}".format(sys.version.replace("\n", " ")),
        "implementacja: {} {}".format(platform.python_implementation(), platform.python_version()),
        "system: {} {} ({})".format(platform.system(), platform.release(), platform.machine()),
        "procesor: {}".format(cpu_model()),
        "zegar perf_counter: monotoniczny={}, rozdzielczość={} s".format(
            clock.monotonic, clock.resolution),
        "jednostka wszystkich czasów w tabelach: nanosekundy (ns)",
    ]


def run():
    os.makedirs(params.RESULTS_DIR, exist_ok=True)

    lfsr_path = os.path.join(params.RESULTS_DIR, "lfsr_numbers_main.txt")
    lcg_path = os.path.join(params.RESULTS_DIR, "lcg_numbers_main.txt")
    sources = {"LFSR": read_numbers(lfsr_path), "LCG": read_numbers(lcg_path)}

    # Lista liczb pierwszych budowana przed pomiarami (punkt 5 w docstringu).
    prepare_primes(isqrt(max(max(values) for values in sources.values())))

    times_by_source, csv_paths, accuracy, rows_by_source = {}, {}, {}, {}
    for source, numbers in sources.items():
        rows, times, decisions = run_battery(numbers)
        times_by_source[source] = times
        rows_by_source[source] = rows
        csv_paths[source] = write_csv(
            os.path.join(params.RESULTS_DIR, "primality_calls_{}.csv".format(source.lower())),
            ["zrodlo", "pozycja", "n", "test", "wynik_pierwsza", "czas_ns"],
            [[source] + row for row in rows],
        )
        unique, truth, summary = accuracy_over_unique(numbers)
        accuracy[source] = {
            "unique": unique, "truth": truth, "summary": summary,
            "primes": sum(1 for n in unique if truth[n]),
            "decisions": decisions,
        }

    both = sources["LFSR"] + sources["LCG"]
    mr_rows = mr_sweep(both)
    fermat_rows = fermat_sweep(both)
    range_rows, range_details = range_tables()
    edges = edge_case_table()
    liars = liars_table()

    # ---------------------------------------------------------- raport
    text = ["# Testy pierwszości - wyniki pomiarów (zakres grupy 3)", ""]
    text.append("Wszystkie liczby w tym pliku są wynikiem uruchomienia `python3 exp_primality.py`.")
    text.append("")
    text.append("## 0. Warunki pomiaru")
    text.append("")
    for line in environment_lines():
        text.append("* {}".format(line))
    text.append("* liczba iteracji: Fermat s = {}, Miller-Rabin s = {}".format(
        params.FERMAT_ROUNDS, params.MR_ROUNDS))
    text.append("* ziarno losowania podstaw: `random.Random({})`, tworzone od nowa dla każdego "
                "testu i scenariusza".format(params.RNG_SEED))
    text.append("* dane wejściowe: `{}` (K = {}) oraz `{}` (K = {})".format(
        lfsr_path, len(sources["LFSR"]), lcg_path, len(sources["LCG"])))
    text.append("* czasy mierzone dla każdej pozycji pliku (także dla liczb powtórzonych); "
                "trafność liczona na zbiorze unikalnych liczb")
    text.append("* przed każdym mierzonym przebiegiem wykonywana jest rozgrzewka "
                "(te same testy bez pomiaru, z osobnym generatorem podstaw)")
    text.append("* każdy czas to JEDNO wywołanie funkcji - dla najkrótszych wywołań "
                "(rzędu mikrosekundy) szum pomiarowy jest rzędu dziesiątek-setek ns, "
                "dlatego istotna jest mediana, a nie pojedyncze maksimum")
    text.append("")
    text.append("## 1. Statystyki czasu (ns) - osobno dla każdego testu i źródła")
    text.append("")
    text.append(markdown_table(
        ["źródło", "test", "liczba pomiarów", "min", "max", "średnia", "mediana"],
        stats_table(times_by_source)))
    text.append("")
    text.append("Pliki z czasem KAŻDEGO wywołania: " + ", ".join(
        "`{}`".format(path) for path in csv_paths.values()))
    text.append("")
    text.append("### 1b. Dlaczego sama mediana jest tu myląca - rozkład dwumodalny")
    text.append("")
    text.append("Czas testu zależy przede wszystkim od tego, czy liczba kończy się na warunku")
    text.append("brzegowym (parzysta - jedno dzielenie), czy wymaga pełnego testu. Przy około")
    text.append("połowie liczb parzystych mediana całego zbioru wypada dokładnie na granicy")
    text.append("dwóch skupień, więc reaguje na drobną zmianę proporcji parzystych. Dlatego")
    text.append("poniżej te same pomiary rozbite są na grupy.")
    text.append("")
    text.append(markdown_table(
        ["źródło", "test", "grupa liczb", "liczba pomiarów", "min ns", "max ns",
         "średnia ns", "mediana ns"],
        group_stats_table(rows_by_source, {src: accuracy[src]["truth"] for src in rows_by_source})))
    text.append("")
    text.append("## 2. Rzeczywisty status pierwszości i błędne decyzje")
    text.append("")
    text.append("Podstawa odniesienia: dokładny test dzielenia przez liczby pierwsze do floor(sqrt(n)).")
    text.append("")
    rows = []
    for source in sources:
        data = accuracy[source]
        for name in ("Fermat", "Miller-Rabin"):
            summary = data["summary"][name]
            rows.append([
                source, name, summary["unique"], summary["primes"], summary["composites"],
                len(summary["pseudoprime"]), len(summary["pseudocomposite"]),
                ", ".join(map(str, summary["pseudoprime"][:10])) or "brak",
            ])
    text.append(markdown_table(
        ["źródło", "test", "liczb unikalnych", "pierwszych", "złożonych",
         "pseudopierwsze (fałszywie pierwsza)", "pseudozłożone (fałszywie złożona)",
         "przykłady pseudopierwszych"], rows))
    text.append("")
    text.append("Zero pseudozłożonych nie jest przypadkiem: oba testy orzekają \"złożona\" tylko")
    text.append("na podstawie kontrprzykładu (podstawa świadcząca o złożoności), a dla liczby")
    text.append("pierwszej taki kontrprzykład nie istnieje. Poprawnie zaimplementowany test")
    text.append("Fermata i Millera-Rabina NIE MOŻE odrzucić liczby pierwszej - każde takie")
    text.append("wystąpienie wskazywałoby na błąd implementacji, nie na własność testu.")
    text.append("")
    text.append("## 3. Przypadki brzegowe i liczby trudne dla testu Fermata")
    text.append("")
    text.append(markdown_table(
        ["n", "dzielenie (dokładnie)", "Fermat", "Miller-Rabin", "Fermat zgodny?",
         "M-R zgodny?", "uwaga"], edges))
    text.append("")
    text.append("## 4. Podstawy mylące testy - przeliczenie wyczerpujące (liczby Carmichaela)")
    text.append("")
    text.append("Dla każdej podstawy t z {2, ..., n-2} sprawdzono jedną iterację testu.")
    text.append("Kolumna ostatnia: prawdopodobieństwo, że test Fermata z s = {} losowymi".format(
        params.FERMAT_ROUNDS))
    text.append("podstawami uzna liczbę za pierwszą (iloraz kłamców podniesiony do potęgi s).")
    text.append("")
    text.append(markdown_table(
        ["n", "liczba podstaw", "kłamcy Fermata", "% kłamców Fermata", "kłamcy M-R",
         "% kłamców M-R", "P(Fermat się myli) [%]"], liars))
    text.append("")
    text.append("## 5. Wpływ liczby iteracji")
    text.append("")
    text.append("Dane: {} unikalnych liczb z obu generatorów (LFSR + LCG, przedział [{}, {}]).".format(
        len(set(both)), params.LOW, params.HIGH))
    text.append("")
    text.append("### Miller-Rabin")
    text.append("")
    text.append(markdown_table(
        ["s (iteracje)", "liczba pomiarów", "min ns", "max ns", "średnia ns", "mediana ns",
         "pseudopierwsze", "pseudozłożone", "które liczby uznane za pierwsze mimo złożoności"],
        mr_rows))
    text.append("")
    text.append("### Fermat (dla porównania, te same dane)")
    text.append("")
    text.append(markdown_table(
        ["s (iteracje)", "liczba pomiarów", "min ns", "max ns", "średnia ns", "mediana ns",
         "pseudopierwsze", "pseudozłożone", "które liczby uznane za pierwsze mimo złożoności"],
        fermat_rows))
    text.append("")
    text.append("## 6. Wpływ przedziału i rozmiaru liczb")
    text.append("")
    text.append("Dla każdego przedziału: {} liczb z LFSR (n = {}) + {} liczb z LCG o m = 2^48".format(
        params.RANGE_K, params.LFSR_N, params.RANGE_K))
    text.append("(parametry Java - generator o m = {} nie pokrywa szerokich przedziałów;".format(
        params.LCG_M))
    text.append("to świadoma zmiana parametru, odnotowana, żeby nie mylić jej ze scenariuszem głównym).")
    text.append("")
    text.append(markdown_table(
        ["przedział", "span", "test", "liczba pomiarów", "min ns", "max ns", "średnia ns",
         "mediana ns"], range_rows))
    text.append("")
    text.append("Udział liczb pierwszych w każdym przedziale (wg dokładnego dzielenia):")
    text.append("")
    text.append(markdown_table(["przedział", "liczb", "pierwszych", "% pierwszych"], range_details))
    text.append("")
    analysis_path = write_text(os.path.join(params.RESULTS_DIR, "primality_analysis.md"),
                               "\n".join(text))
    write_text(os.path.join(params.RESULTS_DIR, "environment.txt"), "\n".join(environment_lines()))

    return {
        "sources": {name: len(values) for name, values in sources.items()},
        "times": times_by_source, "accuracy": accuracy, "csv": csv_paths,
        "analysis_path": analysis_path, "mr_sweep": mr_rows, "fermat_sweep": fermat_rows,
        "ranges": range_rows, "edges": edges, "liars": liars,
    }


if __name__ == "__main__":
    summary = run()
    for source, times in summary["times"].items():
        for name in TESTS:
            stats = time_stats(times[name])
            print("{:5s} {:13s} n={:3d} min={:8d} ns mediana={:10.1f} ns".format(
                source, name, stats["n"], stats["min_ns"], stats["median_ns"]))
    for source, data in summary["accuracy"].items():
        for name in ("Fermat", "Miller-Rabin"):
            item = data["summary"][name]
            print("{:5s} {:13s} pseudopierwsze={} pseudozłożone={} (unikalnych {})".format(
                source, name, len(item["pseudoprime"]), len(item["pseudocomposite"]), item["unique"]))
    print("analiza: {}".format(summary["analysis_path"]))
