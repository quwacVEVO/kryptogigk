"""Eksperymenty dla generatora LCG (zakres grupy 2).

Uruchomienie:  python3 exp_lcg.py
Wyniki:        results/lcg_*.txt, results/lcg_analysis.md, results/lcg_variants.csv
"""

import os

import params
from common import (collision_report, markdown_table, minimal_period_of_block, write_csv,
                    write_numbers, write_text)
from lcg import LCG, hull_dobell
from lfsr import check_k_fits_interval

MAX_PERIOD_STEPS = 200_000

# Zestawy parametrów do porównania. Opis mówi o pochodzeniu, a nie o okresie -
# okres jest mierzony albo jawnie oznaczony jako nieustalony (przerwany pomiar).
PARAM_SETS = (
    ("scenariusz główny", params.LCG_M, params.LCG_A, params.LCG_C, params.LCG_X0),
    ("notatka, przykład", 15, 51, 13, 1),
    ("ANSI C", 2 ** 31, 1103515245, 12345, 2026),
    ("Borland C/C++", 2 ** 32, 22695477, 1, 2026),
    ("Microsoft Visual C++", 2 ** 32, 214013, 2531011, 2026),
    ("Microsoft Visual Basic", 2 ** 24, 1140671485, 12820163, 2026),
    ("Java", 2 ** 48, 25214903917, 11, 2026),
    ("pełny okres, małe m", 1024, 5, 1, 7),
    ("c = 0 (multiplikatywny)", 65536, 25173, 0, 2026),
    ("a = 1 (licznik modulo m)", 65536, 1, 13849, 2026),
    ("a = 0 (stała)", 65536, 0, 13849, 2026),
    ("a = 2, c = 0 (zbiega do 0)", 65536, 2, 0, 2026),
    ("m nie jest potęgą 2", 1000, 21, 3, 7),
)

X0_VARIANTS = (0, 1, 2026, 12345, 65535)

MAPPING_SCENARIOS = (
    (1, 1000, "mod_reject"),
    (1, 1000, "mod"),
    (1, 1000, "scale"),
    (1, 1024, "mod_reject"),
    (1, 1024, "mod"),
    (1, 1024, "scale"),
)


def main_generator():
    return LCG(m=params.LCG_M, a=params.LCG_A, c=params.LCG_C, x0=params.LCG_X0)


def header_lines(generator, count, low, high, mode, extra=()):
    lines = [
        "LCG - zadanie lab05, grupa 2 (realizacja grupy 5 / GenAI)",
        generator.describe() + "   (c = przyrost, w notatce oznaczany b)",
        "K={} przedzial=[{}, {}] mapowanie={}".format(count, low, high, mode),
    ]
    lines.extend(extra)
    return lines


def measure_value_period(make_generator, low, high, mode, state_period):
    """Minimalny okres ciągu LICZB WYNIKOWYCH, gdy znany jest okres stanu i ogon = 0.

    Blok wartości z jednego pełnego okresu stanu jest pełnym okresem ciągu wartości
    (mapowanie zależy wyłącznie od stanu). Kontrola: następny blok musi być identyczny.
    """
    if not state_period or state_period > MAX_PERIOD_STEPS:
        return None, False
    span = high - low + 1
    generator = make_generator()

    def block_over_period():
        """Wartości z dokładnie `state_period` kolejnych stanów."""
        block = []
        usable = generator.m - (generator.m % span)
        for _ in range(state_period):
            state = generator.next_value()
            if mode == "mod_reject":
                if state < usable:
                    block.append(low + state % span)
            elif mode == "mod":
                block.append(low + state % span)
            else:
                block.append(low + (state * span) // generator.m)
        return block

    first = block_over_period()
    confirmed = first == block_over_period()
    return (minimal_period_of_block(first) if confirmed else None), confirmed


def describe_hull_dobell(m, a, c):
    ok, checks = hull_dobell(m, a, c)
    failed = [name for name, result, _ in checks if not result]
    if ok:
        return "spełnione"
    return "niespełnione ({})".format("; ".join(failed)) if failed else "nie dotyczy (c = 0)"


def param_table():
    rows = []
    for label, m, a, c, x0 in PARAM_SETS:
        generator = LCG(m=m, a=a, c=c, x0=x0)
        tail, period = generator.period(max_steps=MAX_PERIOD_STEPS)
        generator.reset()
        span = params.HIGH - params.LOW + 1
        if m < span:
            numbers, note = None, "m < span, mapowanie mod_reject niemożliwe"
        else:
            numbers, note = generator.numbers(params.K, params.LOW, params.HIGH,
                                              mode=params.LCG_MAPPING), None
        report = collision_report(numbers) if numbers else None
        rows.append([
            label, m, a, c, x0,
            describe_hull_dobell(m, a, c),
            tail if tail is not None else "?",
            period if period is not None else "> {} (pomiar przerwany)".format(MAX_PERIOD_STEPS),
            "tak" if period == m else "nie" if period is not None else "nie ustalono",
            report["unique"] if report else note,
            report["collisions"] if report else "-",
            numbers[:5] if numbers else "-",
        ])
    return rows


def x0_table():
    rows = []
    for x0 in X0_VARIANTS:
        generator = LCG(m=params.LCG_M, a=params.LCG_A, c=params.LCG_C, x0=x0)
        tail, period = generator.period(max_steps=MAX_PERIOD_STEPS)
        generator.reset()
        numbers = generator.numbers(params.K, params.LOW, params.HIGH, mode=params.LCG_MAPPING)
        report = collision_report(numbers)
        rows.append([x0, tail, period, report["unique"], report["collisions"], numbers[:5]])
    return rows


def mapping_table():
    rows = []
    for low, high, mode in MAPPING_SCENARIOS:
        generator = main_generator()
        tail, period = generator.period(max_steps=MAX_PERIOD_STEPS)
        generator.reset()
        numbers = generator.numbers(params.K, low, high, mode=mode)
        report = collision_report(numbers)
        value_period, confirmed = measure_value_period(main_generator, low, high, mode, period)
        rows.append([
            "[{}, {}]".format(low, high), high - low + 1, mode, period,
            value_period if confirmed else "nie potwierdzono",
            report["unique"], report["collisions"],
            min(numbers), max(numbers),
        ])
    return rows


def run():
    os.makedirs(params.RESULTS_DIR, exist_ok=True)
    out = {}

    # ---------------------------------------------------------- scenariusz główny
    generator = main_generator()
    tail, period = generator.period(max_steps=MAX_PERIOD_STEPS)
    generator.reset()
    numbers = generator.numbers(params.K, params.LOW, params.HIGH, mode=params.LCG_MAPPING)
    report = collision_report(numbers)
    value_period, confirmed = measure_value_period(
        main_generator, params.LOW, params.HIGH, params.LCG_MAPPING, period)
    hd_ok, hd_checks = hull_dobell(params.LCG_M, params.LCG_A, params.LCG_C)

    main_path = os.path.join(params.RESULTS_DIR, "lcg_numbers_main.txt")
    write_numbers(main_path, numbers, header_lines(
        generator, params.K, params.LOW, params.HIGH, params.LCG_MAPPING,
        extra=["okres stanu={} ogon={} okres ciagu wartosci={}".format(period, tail, value_period)]))

    out["main"] = {
        "params": generator.describe(), "tail": tail, "state_period": period,
        "value_period": value_period, "confirmed": confirmed, "collisions": report,
        "path": main_path, "numbers": numbers, "hull_dobell": (hd_ok, hd_checks),
    }

    # ---------------------------------------------------------- K różnych liczb (filtr)
    ok, message = check_k_fits_interval(params.UNIQUE_K, params.LOW, params.HIGH)
    unique_generator = main_generator()
    unique_numbers = unique_generator.unique_numbers(
        params.UNIQUE_K, params.LOW, params.HIGH, mode=params.LCG_MAPPING)
    unique_path = os.path.join(params.RESULTS_DIR, "lcg_numbers_unique.txt")
    write_numbers(unique_path, unique_numbers, header_lines(
        unique_generator, params.UNIQUE_K, params.LOW, params.HIGH, params.LCG_MAPPING,
        extra=["ciag K roznych liczb: filtr powtorzen na ciagu wyjsciowym", message]))
    out["unique_filtered"] = {
        "k": params.UNIQUE_K, "distinct": len(set(unique_numbers)), "message": message,
        "path": unique_path, "head": unique_numbers[:12],
    }

    # ---------------------------------------------------------- ciąg bez kolizji BEZ filtru
    raw_generator = LCG(m=params.LCG_RAW_M, a=params.LCG_RAW_A, c=params.LCG_RAW_C,
                        x0=params.LCG_RAW_X0)
    raw_tail, raw_period = raw_generator.period(max_steps=MAX_PERIOD_STEPS)
    raw_generator.reset()
    raw_numbers = raw_generator.numbers(params.LCG_RAW_K, params.LCG_RAW_LOW,
                                        params.LCG_RAW_HIGH, mode="mod")
    raw_report = collision_report(raw_numbers)
    raw_hd_ok, _ = hull_dobell(params.LCG_RAW_M, params.LCG_RAW_A, params.LCG_RAW_C)
    raw_path = os.path.join(params.RESULTS_DIR, "lcg_numbers_raw_unique.txt")
    write_numbers(raw_path, raw_numbers, header_lines(
        raw_generator, params.LCG_RAW_K, params.LCG_RAW_LOW, params.LCG_RAW_HIGH, "mod",
        extra=["ciag bez kolizji BEZ filtru: pelny okres m={} i span=m (mapowanie bijektywne)".format(
            params.LCG_RAW_M)]))

    # przypadek nasycający ograniczenie: K = b - a + 1
    saturating = raw_generator.reset().numbers(
        params.LCG_RAW_HIGH - params.LCG_RAW_LOW + 1, params.LCG_RAW_LOW, params.LCG_RAW_HIGH,
        mode="mod")
    saturating_report = collision_report(saturating)

    out["unique_raw"] = {
        "params": raw_generator.describe(), "tail": raw_tail, "period": raw_period,
        "hull_dobell": raw_hd_ok, "collisions": raw_report["collisions"],
        "path": raw_path, "head": raw_numbers[:12],
        "saturating_k": len(saturating), "saturating_collisions": saturating_report["collisions"],
    }

    # ---------------------------------------------------------- przypadek niewykonalny
    impossible_ok, impossible_message = check_k_fits_interval(
        params.IMPOSSIBLE_K, params.LOW, params.HIGH)
    error_message = None
    try:
        main_generator().unique_numbers(params.IMPOSSIBLE_K, params.LOW, params.HIGH)
    except ValueError as error:
        error_message = str(error)
    out["impossible"] = {"check": impossible_message, "error": error_message}

    # ---------------------------------------------------------- tabele
    param_rows = param_table()
    x0_rows = x0_table()
    mapping_rows = mapping_table()

    text = ["# LCG - wyniki pomiarów (zakres grupy 2)", ""]
    text.append("Wszystkie liczby w tym pliku są wynikiem uruchomienia `python3 exp_lcg.py`.")
    text.append("Oznaczenia: `c` to przyrost (w notatce `b`), `[a, b]` to przedział `[low, high]`.")
    text.append("")
    text.append("## 1. Scenariusz główny")
    text.append("")
    text.append("* parametry: `{}`".format(generator.describe()))
    text.append("* K = {}, przedział = [{}, {}] (span = {}), mapowanie = `{}`".format(
        params.K, params.LOW, params.HIGH, params.HIGH - params.LOW + 1, params.LCG_MAPPING))
    text.append("* warunki Hull-Dobella: {}".format("spełnione" if hd_ok else "niespełnione"))
    for name, result, detail in hd_checks:
        text.append("  * {} - {} ({})".format(name, "tak" if result else "nie", detail))
    text.append("* okres STANU zmierzony: {} (ogon {}); m = {}".format(period, tail, params.LCG_M))
    text.append("* okres ciągu WARTOŚCI po mapowaniu: {} (powtórzenie potwierdzone: {})".format(
        value_period, confirmed))
    text.append("* kolizje w K = {} liczbach: {} (różnych wartości {}, najczęstsza krotność {})".format(
        params.K, report["collisions"], report["unique"], report["max_multiplicity"]))
    text.append("* pierwsza kolizja: {}".format(
        "pozycja {} (wartość {})".format(*report["first_collision"])
        if report["first_collision"] else "brak"))
    text.append("* najczęściej powtarzane (wartość, krotność): {}".format(report["top_repeated"]))
    text.append("* plik z liczbami: `{}`".format(main_path))
    text.append("")
    text.append("## 2. Ciąg K różnych liczb")
    text.append("")
    text.append("* warunek wykonalności: {}".format(message))
    text.append("* K = {} różnych liczb z [{}, {}] filtrem powtórzeń: `{}`".format(
        params.UNIQUE_K, params.LOW, params.HIGH, unique_path))
    text.append("* pierwsze 12 wartości: {}".format(unique_numbers[:12]))
    text.append("* ciąg BEZ filtru i bez kolizji: `{}`, K = {}, [{}, {}], mapowanie `mod`".format(
        raw_generator.describe(), params.LCG_RAW_K, params.LCG_RAW_LOW, params.LCG_RAW_HIGH))
    text.append("  * warunki Hull-Dobella: {}; zmierzony okres stanu: {} (ogon {})".format(
        "spełnione" if raw_hd_ok else "niespełnione", raw_period, raw_tail))
    text.append("  * kolizje: {}; plik: `{}`".format(raw_report["collisions"], raw_path))
    text.append("  * pierwsze 12 wartości: {}".format(raw_numbers[:12]))
    text.append("  * przypadek nasycający ograniczenie K = b-a+1 = {}: kolizji {}".format(
        out["unique_raw"]["saturating_k"], out["unique_raw"]["saturating_collisions"]))
    text.append("* przypadek niewykonalny K = {}: {}".format(params.IMPOSSIBLE_K, impossible_message))
    text.append("* reakcja implementacji: `ValueError: {}`".format(error_message))
    text.append("")
    text.append("## 3. Wpływ parametrów m, a, c, x0")
    text.append("")
    text.append("Kolumny \"różnych w K=200\" i \"kolizji\" dotyczą przedziału [{}, {}] i mapowania `{}`.".format(
        params.LOW, params.HIGH, params.LCG_MAPPING))
    text.append("Pomiar okresu przerywany po {} krokach - wtedy okres jest nieustalony, a nie \"duży\".".format(
        MAX_PERIOD_STEPS))
    text.append("")
    text.append(markdown_table(
        ["zestaw", "m", "a", "c", "x0", "Hull-Dobell", "ogon", "okres stanu (zmierzony)",
         "okres = m?", "różnych w K=200", "kolizji", "pierwsze 5 liczb"], param_rows))
    text.append("")
    text.append("## 4. Wpływ ziarna x0 (m = {}, a = {}, c = {})".format(
        params.LCG_M, params.LCG_A, params.LCG_C))
    text.append("")
    text.append(markdown_table(
        ["x0", "ogon", "okres stanu", "różnych w K=200", "kolizji", "pierwsze 5 liczb"], x0_rows))
    text.append("")
    text.append("## 5. Wpływ sposobu mapowania na przedział")
    text.append("")
    text.append("Ten sam generator (scenariusz główny), różne przedziały i tryby mapowania.")
    text.append("")
    text.append(markdown_table(
        ["przedział", "span", "tryb", "okres stanu", "okres wartości", "różnych w K=200",
         "kolizji", "min", "max"], mapping_rows))
    text.append("")
    analysis_path = write_text(os.path.join(params.RESULTS_DIR, "lcg_analysis.md"), "\n".join(text))

    csv_path = write_csv(
        os.path.join(params.RESULTS_DIR, "lcg_variants.csv"),
        ["zestaw", "m", "a", "c", "x0", "hull_dobell", "ogon", "okres_stanu", "roznych_w_K", "kolizje"],
        [[r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[9], r[10]] for r in param_rows],
    )

    out["tables"] = {"params": param_rows, "x0": x0_rows, "mapping": mapping_rows}
    out["analysis_path"] = analysis_path
    out["csv_path"] = csv_path
    return out


if __name__ == "__main__":
    summary = run()
    print("LCG: {}".format(summary["main"]["params"]))
    print("  okres stanu: {} (ogon {}), okres wartości: {}".format(
        summary["main"]["state_period"], summary["main"]["tail"], summary["main"]["value_period"]))
    print("  kolizje w K={}: {} (różnych {})".format(
        params.K, summary["main"]["collisions"]["collisions"], summary["main"]["collisions"]["unique"]))
    print("  pliki: {}, {}, {}".format(
        summary["main"]["path"], summary["unique_filtered"]["path"], summary["unique_raw"]["path"]))
    print("  analiza: {} oraz {}".format(summary["analysis_path"], summary["csv_path"]))
