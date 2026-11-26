"""Wspólne narzędzia: zapis/odczyt plików z liczbami, kolizje, cykle, statystyki.

Moduł celowo korzysta tylko z biblioteki standardowej Pythona.
Definicje i konwencje opisane są w README.md (sekcja "Ustalenia i parametry").
"""

import os
import statistics
import time
from collections import Counter

COMMENT_PREFIX = "#"


class BadNumberFile(ValueError):
    """Plik z liczbami istnieje, ale ma niepoprawną treść (zły format, brak danych)."""


# ---------------------------------------------------------------- pliki

def write_numbers(path, numbers, header=()):
    """Zapisuje liczby po jednej w wierszu; wiersze nagłówka poprzedza znakiem '#'.

    Nagłówek służy do zapisania parametrów generatora razem z danymi, żeby
    plik wynikowy był samoopisujący się (potrzebne do odtworzenia eksperymentu).
    """
    folder = os.path.dirname(path)
    if folder:
        os.makedirs(folder, exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        for line in header:
            handle.write("{} {}\n".format(COMMENT_PREFIX, line))
        for value in numbers:
            handle.write("{}\n".format(value))
    return path


def read_numbers(path):
    """Czyta liczby całkowite (po jednej w wierszu); pomija puste wiersze i komentarze.

    Brak pliku i błędny format danych są rozróżnione i opisane komunikatem
    wskazującym plik oraz numer wiersza (wymaganie dodatkowe grup 1 i 2).
    """
    try:
        with open(path, encoding="utf-8") as handle:
            lines = handle.readlines()
    except FileNotFoundError:
        raise FileNotFoundError("Brak pliku z danymi: {}".format(path)) from None
    except IsADirectoryError:
        raise BadNumberFile("Ścieżka wskazuje katalog, nie plik: {}".format(path)) from None
    except UnicodeDecodeError:
        raise BadNumberFile("Plik nie jest tekstem UTF-8: {}".format(path)) from None

    numbers = []
    for line_no, line in enumerate(lines, start=1):
        text = line.strip()
        if not text or text.startswith(COMMENT_PREFIX):
            continue
        try:
            numbers.append(int(text))
        except ValueError:
            raise BadNumberFile(
                "{}:{}: oczekiwano liczby całkowitej, jest {!r}".format(path, line_no, text)
            ) from None
    if not numbers:
        raise BadNumberFile("{}: plik nie zawiera żadnej liczby".format(path))
    return numbers


# ---------------------------------------------------------------- kolizje

def collision_report(numbers):
    """Statystyka powtórzeń w ciągu LICZB WYNIKOWYCH (nie stanów generatora).

    Definicja kolizji przyjęta w projekcie: kolizja to pozycja ciągu, której
    wartość wystąpiła już wcześniej. Zatem
        liczba kolizji = len(numbers) - liczba różnych wartości,
    czyli wartość występująca k razy wnosi k-1 kolizji.
    """
    counts = Counter(numbers)
    repeated = {value: n for value, n in counts.items() if n > 1}

    first_collision = None
    seen = set()
    for index, value in enumerate(numbers):
        if value in seen:
            first_collision = (index, value)
            break
        seen.add(value)

    return {
        "count": len(numbers),
        "unique": len(counts),
        "collisions": len(numbers) - len(counts),
        "repeated_values": len(repeated),
        "max_multiplicity": max(counts.values()) if counts else 0,
        "first_collision": first_collision,
        "top_repeated": sorted(repeated.items(), key=lambda item: (-item[1], item[0]))[:5],
    }


# ---------------------------------------------------------------- cykle

def find_cycle(start, step, max_steps=200_000):
    """Długość części przedcyklicznej (ogona) i długość cyklu ciągu stanów.

    Ciąg stanów: s_0 = start, s_{i+1} = step(s_i); stan musi być haszowalny.
    Metoda: słownik "stan -> numer kroku pierwszego wystąpienia"; gdy stan się
    powtórzy, ogon = indeks pierwszego wystąpienia, cykl = bieżący indeks - ogon.
    Zwraca (ogon, cykl) albo (None, None), gdy w max_steps krokach stan się nie powtórzył.
    """
    first_seen = {}
    state = start
    index = 0
    while index <= max_steps:
        if state in first_seen:
            tail = first_seen[state]
            return tail, index - tail
        first_seen[state] = index
        state = step(state)
        index += 1
    return None, None


def divisors(number):
    """Rosnąco posortowane dzielniki liczby naturalnej."""
    found = set()
    index = 1
    while index * index <= number:
        if number % index == 0:
            found.add(index)
            found.add(number // index)
        index += 1
    return sorted(found)


def minimal_period_of_block(block):
    """Najmniejszy okres ciągu, o którym wiadomo, że `block` jest jego pełnym okresem.

    Minimalny okres musi dzielić długość bloku, więc wystarczy sprawdzić dzielniki.
    """
    if not block:
        return 0
    length = len(block)
    for candidate in divisors(length):
        if all(block[i] == block[(i + candidate) % length] for i in range(length)):
            return candidate
    return length


def sequence_period(values):
    """Najmniejszy okres p taki, że values[i] == values[i+p] dla wszystkich i.

    Używane tylko do ciągów pokrywających co najmniej dwa pełne cykle; dla
    krótszych danych zwraca None (brak dowodu okresowości).
    """
    n = len(values)
    for period in range(1, n // 2 + 1):
        if all(values[i] == values[i + period] for i in range(n - period)):
            return period
    return None


# ---------------------------------------------------------------- statystyki i pomiar czasu

def time_stats(samples_ns):
    """Minimum, maksimum, średnia i mediana dla listy czasów w nanosekundach."""
    if not samples_ns:
        return {"n": 0, "min_ns": None, "max_ns": None, "mean_ns": None, "median_ns": None}
    return {
        "n": len(samples_ns),
        "min_ns": min(samples_ns),
        "max_ns": max(samples_ns),
        "mean_ns": statistics.fmean(samples_ns),
        "median_ns": statistics.median(samples_ns),
    }


def measure_ns(function, *args, **kwargs):
    """Mierzy czas jednego wywołania zegarem monotonicznym time.perf_counter_ns.

    Zwraca (wynik, czas_w_ns). Mierzony jest wyłącznie czas wywołania funkcji
    testującej - bez wczytywania plików i bez przygotowania danych.
    """
    start = time.perf_counter_ns()
    result = function(*args, **kwargs)
    elapsed = time.perf_counter_ns() - start
    return result, elapsed


# ---------------------------------------------------------------- tabele i zapis wyników

def markdown_table(headers, rows):
    """Prosta tabela Markdown (bez wyrównywania szerokości kolumn)."""
    out = ["| " + " | ".join(str(h) for h in headers) + " |",
           "|" + "|".join(["---"] * len(headers)) + "|"]
    for row in rows:
        out.append("| " + " | ".join("" if c is None else str(c) for c in row) + " |")
    return "\n".join(out)


def write_text(path, text):
    """Zapisuje tekst (raport/tabele) do pliku, tworząc katalog docelowy."""
    folder = os.path.dirname(path)
    if folder:
        os.makedirs(folder, exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(text if text.endswith("\n") else text + "\n")
    return path


def write_csv(path, headers, rows):
    """Zapisuje dane pomiarowe w formacie CSV (separator ',')."""
    import csv

    folder = os.path.dirname(path)
    if folder:
        os.makedirs(folder, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(headers)
        writer.writerows(rows)
    return path
