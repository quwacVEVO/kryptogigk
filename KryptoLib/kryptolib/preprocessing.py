"""Przygotowanie tekstu (część 1): funkcje czyszczące, formatowanie, kolumny,
operacje na plikach oraz tryby standaryzacji ALFA26 i ALFA37.
"""

import re
import unicodedata


# =====================================================================
# 1. FUNKCJE CZYSZCZĄCE
# =====================================================================

# Litery, które nie rozkładają się w NFD na literę bazową + akcent
_SPECJALNE = str.maketrans({
    "ł": "l", "Ł": "L", "ø": "o", "Ø": "O", "đ": "d", "Đ": "D",
    "ß": "ss", "æ": "ae", "Æ": "AE", "œ": "oe", "Œ": "OE",
})


def usun_biale_znaki(tekst: str) -> str:
    """Usuwa wszystkie białe znaki (spacje, tabulatory, znaki nowej linii)."""
    return re.sub(r"\s+", "", tekst)


def usun_znaki_diakrytyczne(tekst: str) -> str:
    """Zamienia znaki diakrytyczne na podstawowe odpowiedniki (ą -> a, Ł -> L, ø -> o, ß -> ss)."""
    tekst = tekst.translate(_SPECJALNE)
    rozlozony = unicodedata.normalize("NFD", tekst)
    bez_akcentow = "".join(c for c in rozlozony if unicodedata.category(c) != "Mn")
    return unicodedata.normalize("NFC", bez_akcentow)


def usun_cyfry(tekst: str) -> str:
    """Usuwa wszystkie cyfry z tekstu."""
    return re.sub(r"\d", "", tekst)


def usun_interpunkcje(tekst: str) -> str:
    """Usuwa znaki interpunkcyjne i symbole (kategorie Unicode P* i S*).

    Obejmuje m.in. . , ! ? : ; - ( ) [ ] @ # $ % + = < > oraz „ ” « » … — – →.
    Zachowuje litery, cyfry i białe znaki.
    """
    return "".join(c for c in tekst if unicodedata.category(c)[0] not in "PS")


def pelne_czyszczenie(tekst: str) -> str:
    """Usuwa diakrytyki, interpunkcję, cyfry i wszystkie białe znaki."""
    tekst = usun_znaki_diakrytyczne(tekst)
    tekst = usun_interpunkcje(tekst)
    tekst = usun_cyfry(tekst)
    return usun_biale_znaki(tekst)


# =====================================================================
# 2. FORMATOWANIE I PODZIAŁ NA KOLUMNY
# =====================================================================

def formatuj_wielkosc_liter(tekst: str, na_wielkie: bool = True) -> str:
    """Zamienia tekst na wielkie (domyślnie) lub małe litery."""
    return tekst.upper() if na_wielkie else tekst.lower()


def podziel_na_kolumny(tekst: str, kolumny: int = 7, grupy: int = 5) -> str:
    """Dzieli tekst na bloki po `grupy` znaków, a bloki układa w wiersze po `kolumny` bloków.

    Domyślnie: wiersze po 7 bloków, każdy blok po 5 liter. Białe znaki w
    tekście wejściowym są pomijane.
    """
    czysty = usun_biale_znaki(tekst)
    bloki = [czysty[i:i + grupy] for i in range(0, len(czysty), grupy)]
    wiersze = [" ".join(bloki[i:i + kolumny]) for i in range(0, len(bloki), kolumny)]
    return "\n".join(wiersze)


# =====================================================================
# 3. WCZYTYWANIE I ZAPISYWANIE DO PLIKU
# =====================================================================

def wczytaj_z_pliku(sciezka_do_pliku: str) -> str:
    """Wczytuje plik tekstowy (UTF-8; ewentualny BOM z Notatnika jest pomijany)."""
    with open(sciezka_do_pliku, "r", encoding="utf-8-sig") as f:
        return f.read()


def zapisz_do_pliku(sciezka_do_pliku: str, tekst: str) -> None:
    """Zapisuje tekst do pliku tekstowego (UTF-8)."""
    with open(sciezka_do_pliku, "w", encoding="utf-8") as f:
        f.write(tekst)


# =====================================================================
# TRYBY STANDARYZACJI: ALFA26 ORAZ ALFA37
# =====================================================================

def tryb_alfa26(tekst: str) -> str:
    """ALFA26: tylko 26 dużych liter A-Z (bez cyfr, spacji, interpunkcji i diakrytyków)."""
    tekst = formatuj_wielkosc_liter(usun_znaki_diakrytyczne(tekst), na_wielkie=True)
    return re.sub(r"[^A-Z]", "", tekst)


def tryb_alfa37(tekst: str) -> str:
    """ALFA37: 26 dużych liter, 10 cyfr i pojedyncze spacje (37 znaków).

    Usuwa diakrytyki i interpunkcję; ciągi białych znaków (także powstałe po
    usunięciu znaków) zamienia w jedną spację; spacje na brzegach są obcinane.
    """
    tekst = formatuj_wielkosc_liter(usun_znaki_diakrytyczne(tekst), na_wielkie=True)
    tekst = re.sub(r"[^A-Z0-9\s]", "", tekst)
    return re.sub(r"\s+", " ", tekst).strip()


def przygotuj_tekst(tekst: str, tryb: str = "ALFA26") -> str:
    """Przygotowuje tekst do szyfrowania w podanym trybie ('ALFA26' lub 'ALFA37')."""
    if tryb.upper() == "ALFA26":
        return tryb_alfa26(tekst)
    if tryb.upper() == "ALFA37":
        return tryb_alfa37(tekst)
    raise ValueError(f"Nieznany tryb '{tryb}'. Dostępne: ALFA26, ALFA37.")
