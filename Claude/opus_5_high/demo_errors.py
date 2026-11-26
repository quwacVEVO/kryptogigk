"""Demonstracja kontroli błędów (wymagania dodatkowe grup 1 i 2).

Uruchomienie:  python3 demo_errors.py
Wynik:         results/error_handling.md - lista faktycznie wywołanych błędów
               wraz z komunikatami, które zobaczy użytkownik.

Każdy przypadek jest tu naprawdę wywoływany, a nie opisany - plik wynikowy
zawiera dokładnie te komunikaty, które zgłosiła implementacja.
"""

import os
import tempfile

import params
from common import BadNumberFile, markdown_table, read_numbers, write_text
from lcg import LCG
from lfsr import LFSR


def attempt(description, function):
    """Wywołuje funkcję i zwraca wiersz tabeli: opis, typ wyjątku, komunikat."""
    try:
        function()
    except Exception as error:  # celowo szeroko - demonstrujemy typ i komunikat
        return [description, type(error).__name__, str(error)]
    return [description, "BRAK WYJĄTKU", "UWAGA: ten przypadek nie został odrzucony"]


def parameter_cases():
    return [
        attempt("LFSR: długość rejestru n = 1", lambda: LFSR(1, [1], [1])),
        attempt("LFSR: n niecałkowite", lambda: LFSR(4.0, [1, 1, 0, 0], [0, 0, 0, 1])),
        attempt("LFSR: wektor odczepów krótszy niż n", lambda: LFSR(4, [1, 1], [0, 0, 0, 1])),
        attempt("LFSR: ziarno dłuższe niż n", lambda: LFSR(4, [1, 1, 0, 0], [0, 0, 0, 1, 1])),
        attempt("LFSR: wartość 2 w wektorze odczepów", lambda: LFSR(3, [1, 2, 0], [0, 0, 1])),
        attempt("LFSR: wszystkie odczepy zerowe", lambda: LFSR(4, [0, 0, 0, 0], [1, 0, 0, 1])),
        attempt("LFSR: ziarno zerowe (bez jawnej zgody)", lambda: LFSR(4, [1, 1, 0, 0], [0] * 4)),
        attempt("LFSR: indeks odczepu poza zakresem", lambda: LFSR.from_tap_indices(4, [0, 9], 1)),
        attempt("LFSR: ziarno nie mieści się w rejestrze",
                lambda: LFSR.from_tap_indices(4, [0, 1], 16)),
        attempt("LFSR: pusty przedział [10, 1]",
                lambda: LFSR.from_tap_indices(16, (0, 2, 3, 5), 1).numbers(5, 10, 1)),
        attempt("LFSR: nieznany tryb mapowania",
                lambda: LFSR.from_tap_indices(16, (0, 2, 3, 5), 1).numbers(5, 1, 10, mode="xyz")),
        attempt("LFSR: K = 1500 różnych liczb z [1, 1000]",
                lambda: LFSR.from_tap_indices(16, (0, 2, 3, 5), 1).unique_numbers(1500, 1, 1000)),
        attempt("LFSR: okres 15 nie pokryje 100 różnych liczb z [1, 1000]",
                lambda: LFSR(4, [1, 1, 0, 0], [0, 0, 0, 1]).unique_numbers(100, 1, 1000)),
        attempt("LCG: moduł m = 1", lambda: LCG(m=1, a=5, c=1, x0=0)),
        attempt("LCG: m niecałkowite", lambda: LCG(m=100.0, a=5, c=1, x0=0)),
        attempt("LCG: a ujemne", lambda: LCG(m=100, a=-5, c=1, x0=0)),
        attempt("LCG: c ujemne", lambda: LCG(m=100, a=5, c=-1, x0=0)),
        attempt("LCG: ziarno x0 = m (poza zakresem)", lambda: LCG(m=100, a=5, c=1, x0=100)),
        attempt("LCG: parametr tekstowy", lambda: LCG(m=100, a="5", c=1, x0=0)),
        attempt("LCG: m = 15 mniejsze od szerokości przedziału (tryb mod_reject)",
                lambda: LCG(m=15, a=51, c=13, x0=1).numbers(10, 1, 1000, mode="mod_reject")),
        attempt("LCG: K = 1500 różnych liczb z [1, 1000]",
                lambda: LCG(m=params.LCG_M, a=params.LCG_A, c=params.LCG_C,
                            x0=params.LCG_X0).unique_numbers(1500, 1, 1000)),
        attempt("LCG: krótki okres nie pokryje przedziału",
                lambda: LCG(m=15, a=51, c=13, x0=1).unique_numbers(100, 1, 1000, mode="scale")),
    ]


def file_cases():
    folder = tempfile.mkdtemp(prefix="lab05_demo_")

    bad_format = os.path.join(folder, "zle_dane.txt")
    with open(bad_format, "w", encoding="utf-8") as handle:
        handle.write("17\n23\nsiedem\n41\n")

    float_format = os.path.join(folder, "liczby_rzeczywiste.txt")
    with open(float_format, "w", encoding="utf-8") as handle:
        handle.write("3.14\n")

    empty = os.path.join(folder, "pusty.txt")
    with open(empty, "w", encoding="utf-8") as handle:
        handle.write("# tylko komentarz, brak liczb\n")

    binary = os.path.join(folder, "binarny.bin")
    with open(binary, "wb") as handle:
        handle.write(b"\xff\xfe\x00\x01")

    return [
        attempt("odczyt: plik nie istnieje",
                lambda: read_numbers(os.path.join(folder, "nie_ma_mnie.txt"))),
        attempt("odczyt: ścieżka wskazuje katalog", lambda: read_numbers(folder)),
        attempt("odczyt: wiersz 3 nie jest liczbą całkowitą", lambda: read_numbers(bad_format)),
        attempt("odczyt: liczba zmiennoprzecinkowa zamiast całkowitej",
                lambda: read_numbers(float_format)),
        attempt("odczyt: plik bez żadnej liczby", lambda: read_numbers(empty)),
        attempt("odczyt: plik binarny (nie UTF-8)", lambda: read_numbers(binary)),
    ]


def run():
    os.makedirs(params.RESULTS_DIR, exist_ok=True)
    parameters = parameter_cases()
    files = file_cases()

    text = ["# Kontrola błędów - faktycznie wywołane przypadki", ""]
    text.append("Plik generowany przez `python3 demo_errors.py`. Każdy wiersz powstał przez")
    text.append("rzeczywiste wywołanie podanej operacji; kolumna \"komunikat\" to dokładna treść")
    text.append("zgłoszona przez implementację.")
    text.append("")
    text.append("## 1. Niepoprawne parametry generatorów")
    text.append("")
    text.append(markdown_table(["przypadek", "wyjątek", "komunikat"], parameters))
    text.append("")
    text.append("## 2. Odczyt pliku z liczbami: brak pliku i błędny format")
    text.append("")
    text.append(markdown_table(["przypadek", "wyjątek", "komunikat"], files))
    text.append("")
    not_caught = [row for row in parameters + files if row[1] == "BRAK WYJĄTKU"]
    text.append("Przypadków, które NIE zostały odrzucone: {}.".format(len(not_caught)))
    for row in not_caught:
        text.append("* {}".format(row[0]))
    text.append("")
    path = write_text(os.path.join(params.RESULTS_DIR, "error_handling.md"), "\n".join(text))
    return {"cases": len(parameters) + len(files), "not_caught": len(not_caught), "path": path}


if __name__ == "__main__":
    summary = run()
    print("przypadków błędnych: {}, nieodrzuconych: {}".format(
        summary["cases"], summary["not_caught"]))
    print("wynik: {}".format(summary["path"]))
