"""Eksperymenty dla generatora LFSR (zakres grupy 1).

Uruchomienie:  python3 exp_lfsr.py
Wyniki:        results/lfsr_*.txt, results/lfsr_analysis.md, results/lfsr_variants.csv

Skrypt nie zawiera interpretacji - liczby i tabele trafiają do plików wynikowych,
a wnioski (z odwołaniem do tych liczb) są w REPORT.md.
"""

import os
from math import gcd

import params
from common import (collision_report, markdown_table, minimal_period_of_block, write_csv,
                    write_numbers, write_text)
from lfsr import LFSR, bits_needed, check_k_fits_interval, int_from_bits

# Kandydaci na wielomiany o okresie maksymalnym (2^n - 1) dla badania wpływu długości.
# Okres NIE jest zakładany - każdy wiersz tabeli jest mierzony metodą period().
LENGTH_CANDIDATES = {
    4: (0, 1),            # x^4 + x + 1
    8: (0, 2, 3, 4),      # x^8 + x^4 + x^3 + x^2 + 1
    12: (0, 1, 4, 6),     # x^12 + x^6 + x^4 + x + 1
    16: (0, 2, 3, 5),     # x^16 + x^5 + x^3 + x^2 + 1
    20: (0, 3),           # x^20 + x^3 + 1
}

# Konfiguracje odczepów dla n = 16 (porównanie kilku konfiguracji - wymaganie dodatkowe).
TAP_VARIANTS = (
    ((0, 2, 3, 5), "wielomian pierwotny (scenariusz główny)"),
    ((0, 11, 13, 14), "inny wielomian pierwotny"),
    ((0, 1), "wielomian niepierwotny - okres 255 zamiast 65535"),
    ((0, 2), "wielomian niepierwotny - bardzo krótki okres"),
    ((0,), "x^16 + 1 - czysty obrót bitów"),
    ((1, 3), "p_0 = 0 - odwzorowanie nieodwracalne (ogon > 0)"),
    ((5,), "p_0 = 0, jeden odczep - silnie zdegenerowany"),
)

SEED_VARIANTS = (0x0001, 0x00FF, 0xACE1, 0xFFFF, 0x8000, 12345)

MAX_PERIOD_STEPS = 1_200_000


def main_generator():
    """Generator LFSR scenariusza głównego (parametry z params.py)."""
    return LFSR.from_tap_indices(params.LFSR_N, params.LFSR_TAP_INDICES, params.LFSR_SEED)


def header_lines(generator, count, low, high, mode, extra=()):
    lines = [
        "LFSR - zadanie lab05, grupa 1 (realizacja grupy 5 / GenAI)",
        generator.describe(),
        "K={} przedzial=[{}, {}] mapowanie={}".format(count, low, high, mode),
    ]
    lines.extend(extra)
    return lines


def measure_value_period(make_generator, low, high, mode, bit_period):
    """Zmierzony minimalny okres ciągu LICZB WYNIKOWYCH (odrębny od okresu stanu).

    Ciąg słów o szerokości `width` powtarza się po `bit_period / NWD(width, bit_period)`
    słowach, bo dopiero wtedy przesunięcie w strumieniu bitów jest wielokrotnością
    okresu bitów. Ten blok jest więc pełnym okresem ciągu wartości; minimalny okres
    wyznaczamy sprawdzając dzielniki długości bloku. Dodatkowo kontrolujemy, że
    następny blok jest identyczny.
    """
    span = high - low + 1
    width = bits_needed(span)
    if not bit_period or width == 0:
        return None, None, False

    words_period = bit_period // gcd(width, bit_period)
    generator = make_generator()

    def one_block():
        block = []
        for _ in range(words_period):
            value = int_from_bits(generator.bits(width))
            if mode == "reject":
                if value < span:
                    block.append(low + value)
            else:
                block.append(low + value % span)
        return block

    first = one_block()
    confirmed = first == one_block()
    period = minimal_period_of_block(first) if confirmed else None
    return period, words_period, confirmed


def safe_numbers(generator, count, low, high, mode):
    """Generuje liczby, zamieniając ograniczenia mapowania na opis zamiast wyjątku."""
    try:
        return generator.numbers(count, low, high, mode=mode), None
    except RuntimeError as error:
        return None, str(error)


def length_table():
    """Wpływ długości rejestru n (dla każdego n osobny wielomian - patrz kolumna f(x))."""
    rows = []
    for n in sorted(LENGTH_CANDIDATES):
        taps = LENGTH_CANDIDATES[n]
        generator = LFSR.from_tap_indices(n, taps, 1)
        tail, period = generator.period(max_steps=MAX_PERIOD_STEPS)
        maximal = (1 << n) - 1
        ones = None
        if period:
            generator.reset()
            ones = round(generator.ones_ratio(period), 4)
        generator.reset()
        numbers, problem = safe_numbers(generator, params.K, params.LOW, params.HIGH, params.LFSR_MAPPING)
        report = collision_report(numbers) if numbers else None
        rows.append([
            n, ",".join(map(str, taps)), generator.polynomial(), tail, period, maximal,
            "tak" if period == maximal else "nie", ones,
            report["unique"] if report else problem,
            report["collisions"] if report else "-",
        ])
    return rows


def taps_table():
    """Wpływ konfiguracji odczepów przy n = 16 i tym samym ziarnie."""
    rows = []
    for taps, comment in TAP_VARIANTS:
        generator = LFSR.from_tap_indices(params.LFSR_N, taps, params.LFSR_SEED)
        tail, period = generator.period(max_steps=MAX_PERIOD_STEPS)
        ones = None
        if period:
            generator.reset()
            ones = round(generator.ones_ratio(period), 4)
        generator.reset()
        numbers, problem = safe_numbers(generator, params.K, params.LOW, params.HIGH, params.LFSR_MAPPING)
        report = collision_report(numbers) if numbers else None
        value_period = None
        if period and tail == 0:
            value_period, _, confirmed = measure_value_period(
                lambda t=taps: LFSR.from_tap_indices(params.LFSR_N, t, params.LFSR_SEED),
                params.LOW, params.HIGH, params.LFSR_MAPPING, period)
            if not confirmed:
                value_period = None
        rows.append([
            ",".join(map(str, taps)), generator.polynomial(), tail, period, ones,
            value_period if value_period is not None else "nie zmierzono",
            report["unique"] if report else problem,
            report["collisions"] if report else "-",
            comment,
        ])
    return rows


def seed_table():
    """Wpływ ziarna przy stałej długości rejestru i stałych odczepach."""
    rows = []
    for seed in SEED_VARIANTS:
        generator = LFSR.from_tap_indices(params.LFSR_N, params.LFSR_TAP_INDICES, seed)
        tail, period = generator.period(max_steps=MAX_PERIOD_STEPS)
        generator.reset()
        numbers, problem = safe_numbers(generator, params.K, params.LOW, params.HIGH, params.LFSR_MAPPING)
        report = collision_report(numbers) if numbers else None
        rows.append([
            "0x{:04X}".format(seed), format(seed, "016b"), tail, period,
            report["unique"] if report else problem,
            report["collisions"] if report else "-",
            numbers[:5] if numbers else "-",
        ])

    # Przypadek brzegowy: ziarno zerowe (dopuszczone jawnie, normalnie zablokowane wyjątkiem).
    zero = LFSR.from_tap_indices(params.LFSR_N, params.LFSR_TAP_INDICES, 0, allow_zero_seed=True)
    tail, period = zero.period(max_steps=1000)
    zero.reset()
    numbers = zero.numbers(10, params.LOW, params.HIGH, mode=params.LFSR_MAPPING)
    rows.append(["0x0000", format(0, "016b"), tail, period, 1, 9, numbers[:5]])
    return rows


def find_collision_free_seed(count, low, high, max_seeds=4096):
    """Szuka ziarna, dla którego surowy ciąg (bez filtru) nie ma ani jednej kolizji."""
    for seed in range(1, max_seeds + 1):
        generator = LFSR.from_tap_indices(params.LFSR_N, params.LFSR_TAP_INDICES, seed)
        numbers = generator.numbers(count, low, high, mode=params.LFSR_MAPPING)
        if len(set(numbers)) == count:
            return seed, numbers
    return None, None


def run():
    os.makedirs(params.RESULTS_DIR, exist_ok=True)
    out = {}

    # ---------------------------------------------------------- scenariusz główny
    generator = main_generator()
    tail, period = generator.period(max_steps=MAX_PERIOD_STEPS)
    generator.reset()
    numbers = generator.numbers(params.K, params.LOW, params.HIGH, mode=params.LFSR_MAPPING)
    report = collision_report(numbers)
    value_period, words_period, confirmed = measure_value_period(
        main_generator, params.LOW, params.HIGH, params.LFSR_MAPPING, period)

    main_path = os.path.join(params.RESULTS_DIR, "lfsr_numbers_main.txt")
    write_numbers(main_path, numbers, header_lines(
        generator, params.K, params.LOW, params.HIGH, params.LFSR_MAPPING,
        extra=["okres stanu={} ogon={} okres ciagu wartosci={}".format(period, tail, value_period)]))

    out["main"] = {
        "params": generator.describe(), "tail": tail, "state_period": period,
        "value_period": value_period, "words_period": words_period, "confirmed": confirmed,
        "collisions": report, "path": main_path, "numbers": numbers,
    }

    # ---------------------------------------------------------- K różnych liczb (filtr)
    ok, message = check_k_fits_interval(params.UNIQUE_K, params.LOW, params.HIGH)
    unique_generator = main_generator()
    unique_numbers = unique_generator.unique_numbers(
        params.UNIQUE_K, params.LOW, params.HIGH, mode=params.LFSR_MAPPING)
    unique_path = os.path.join(params.RESULTS_DIR, "lfsr_numbers_unique.txt")
    write_numbers(unique_path, unique_numbers, header_lines(
        unique_generator, params.UNIQUE_K, params.LOW, params.HIGH, params.LFSR_MAPPING,
        extra=["ciag K roznych liczb: filtr powtorzen na ciagu wyjsciowym", message]))
    out["unique_filtered"] = {
        "k": params.UNIQUE_K, "distinct": len(set(unique_numbers)),
        "k_fits": ok, "message": message, "path": unique_path,
        "head": unique_numbers[:12],
    }

    # ---------------------------------------------------------- ciąg bez kolizji BEZ filtru
    seed, raw_numbers = find_collision_free_seed(
        params.RAW_UNIQUE_K, params.RAW_UNIQUE_LOW, params.RAW_UNIQUE_HIGH)
    raw_path = os.path.join(params.RESULTS_DIR, "lfsr_numbers_raw_unique.txt")
    if seed is not None:
        raw_generator = LFSR.from_tap_indices(params.LFSR_N, params.LFSR_TAP_INDICES, seed)
        write_numbers(raw_path, raw_numbers, header_lines(
            raw_generator, params.RAW_UNIQUE_K, params.RAW_UNIQUE_LOW, params.RAW_UNIQUE_HIGH,
            params.LFSR_MAPPING,
            extra=["ciag bez kolizji uzyskany BEZ filtru - dobrane ziarno 0x{:04X}".format(seed)]))
    out["unique_raw"] = {
        "k": params.RAW_UNIQUE_K, "low": params.RAW_UNIQUE_LOW, "high": params.RAW_UNIQUE_HIGH,
        "seed": seed, "path": raw_path if seed is not None else None,
        "head": raw_numbers[:12] if raw_numbers else None,
    }

    # ---------------------------------------------------------- przypadek niewykonalny
    impossible_ok, impossible_message = check_k_fits_interval(params.IMPOSSIBLE_K, params.LOW, params.HIGH)
    error_message = None
    try:
        main_generator().unique_numbers(params.IMPOSSIBLE_K, params.LOW, params.HIGH)
    except ValueError as error:
        error_message = str(error)
    out["impossible"] = {"ok": impossible_ok, "check": impossible_message, "error": error_message}

    # ---------------------------------------------------------- tabele wpływu parametrów
    lengths = length_table()
    taps = taps_table()
    seeds = seed_table()

    text = ["# LFSR - wyniki pomiarów (zakres grupy 1)", ""]
    text.append("Wszystkie liczby w tym pliku są wynikiem uruchomienia `python3 exp_lfsr.py`.")
    text.append("Konwencja stanu, odczepów i mapowania: patrz docstring w `lfsr.py` oraz README.md.")
    text.append("")
    text.append("## 1. Scenariusz główny")
    text.append("")
    text.append("* parametry: `{}`".format(generator.describe()))
    text.append("* K = {}, przedział = [{}, {}] (span = {}), mapowanie = `{}`".format(
        params.K, params.LOW, params.HIGH, params.HIGH - params.LOW + 1, params.LFSR_MAPPING))
    text.append("* bitów na jedną liczbę (szerokość słowa): {}".format(
        bits_needed(params.HIGH - params.LOW + 1)))
    text.append("* okres STANU: {} (ogon {}), teoretyczne maksimum 2^{} - 1 = {}".format(
        period, tail, params.LFSR_N, (1 << params.LFSR_N) - 1))
    text.append("* okres ciągu WARTOŚCI (po mapowaniu): {} (blok {} słów, powtórzenie potwierdzone: {})".format(
        value_period, words_period, confirmed))
    text.append("* kolizje w K = {} liczbach: {} (różnych wartości {}, najczęstsza krotność {})".format(
        params.K, report["collisions"], report["unique"], report["max_multiplicity"]))
    text.append("* pierwsza kolizja: pozycja {} (wartość {})".format(
        report["first_collision"][0], report["first_collision"][1])
        if report["first_collision"] else "* pierwsza kolizja: brak")
    text.append("* najczęściej powtarzane wartości (wartość, krotność): {}".format(report["top_repeated"]))
    text.append("* plik z liczbami: `{}`".format(main_path))
    text.append("")
    text.append("## 2. Ciąg K różnych liczb")
    text.append("")
    text.append("* warunek wykonalności: {}".format(message))
    text.append("* K = {} różnych liczb z [{}, {}] uzyskane filtrem powtórzeń: plik `{}`".format(
        params.UNIQUE_K, params.LOW, params.HIGH, unique_path))
    text.append("* pierwsze 12 wartości: {}".format(unique_numbers[:12]))
    if seed is not None:
        text.append("* ciąg BEZ filtru i bez kolizji: K = {}, [{}, {}], dobrane ziarno 0x{:04X}, plik `{}`".format(
            params.RAW_UNIQUE_K, params.RAW_UNIQUE_LOW, params.RAW_UNIQUE_HIGH, seed, raw_path))
        text.append("* pierwsze 12 wartości: {}".format(raw_numbers[:12]))
    else:
        text.append("* nie znaleziono ziarna dającego ciąg bez kolizji bez filtru w przebadanym zakresie ziaren")
    text.append("* przypadek niewykonalny K = {}: {}".format(params.IMPOSSIBLE_K, impossible_message))
    text.append("* reakcja implementacji: `ValueError: {}`".format(error_message))
    text.append("")
    text.append("## 3. Wpływ długości rejestru")
    text.append("")
    text.append("Dla każdego n użyto osobnego zestawu odczepów (kolumna f(x)); ziarno = 1.")
    text.append("")
    text.append(markdown_table(
        ["n", "odczepy j", "f(x)", "ogon", "okres stanu", "2^n-1", "maksymalny?",
         "udział jedynek w okresie", "różnych w K=200", "kolizji"], lengths))
    text.append("")
    text.append("## 4. Wpływ konfiguracji odczepów (n = {}, ziarno = 0x{:04X})".format(
        params.LFSR_N, params.LFSR_SEED))
    text.append("")
    text.append(markdown_table(
        ["odczepy j", "f(x)", "ogon", "okres stanu", "udział jedynek",
         "okres wartości", "różnych w K=200", "kolizji", "uwaga"], taps))
    text.append("")
    text.append("## 5. Wpływ ziarna (n = {}, odczepy {})".format(
        params.LFSR_N, ",".join(map(str, params.LFSR_TAP_INDICES))))
    text.append("")
    text.append(markdown_table(
        ["ziarno", "ziarno (bity)", "ogon", "okres stanu", "różnych w K=200", "kolizji",
         "pierwsze 5 liczb"], seeds))
    text.append("")
    analysis_path = write_text(os.path.join(params.RESULTS_DIR, "lfsr_analysis.md"), "\n".join(text))

    csv_path = write_csv(
        os.path.join(params.RESULTS_DIR, "lfsr_variants.csv"),
        ["grupa", "n", "odczepy", "ziarno", "ogon", "okres_stanu", "roznych_w_K", "kolizje"],
        [["dlugosc", r[0], r[1], 1, r[3], r[4], r[8], r[9]] for r in lengths]
        + [["odczepy", params.LFSR_N, r[0], params.LFSR_SEED, r[2], r[3], r[6], r[7]] for r in taps]
        + [["ziarno", params.LFSR_N, ",".join(map(str, params.LFSR_TAP_INDICES)), r[0], r[2], r[3], r[4], r[5]]
           for r in seeds],
    )

    out["tables"] = {"lengths": lengths, "taps": taps, "seeds": seeds}
    out["analysis_path"] = analysis_path
    out["csv_path"] = csv_path
    return out


if __name__ == "__main__":
    summary = run()
    print("LFSR: {}".format(summary["main"]["params"]))
    print("  okres stanu: {} (ogon {}), okres wartości: {}".format(
        summary["main"]["state_period"], summary["main"]["tail"], summary["main"]["value_period"]))
    print("  kolizje w K={}: {} (różnych {})".format(
        params.K, summary["main"]["collisions"]["collisions"], summary["main"]["collisions"]["unique"]))
    print("  pliki: {}, {}, {}".format(
        summary["main"]["path"], summary["unique_filtered"]["path"], summary["unique_raw"]["path"]))
    print("  analiza: {} oraz {}".format(summary["analysis_path"], summary["csv_path"]))
