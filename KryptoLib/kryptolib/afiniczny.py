"""Szyfr afiniczny E(x) = (a*x + b) mod m w trybach ALFA26 / ALFA37 (część 2).

Funkcje są restrykcyjne tak samo jak szyfr ogólny: tekst musi już składać się
ze znaków alfabetu trybu (użyj preprocessing.przygotuj_tekst). Klucze
afiniczne można też wyrazić jako permutację (klucze.affine_key) i wykonać
szyfrem ogólnym - wyniki są identyczne.
"""

import math

from .alfabety import get_alphabet, sprawdz_tekst


# =====================================================================
# POMOCNICZE FUNKCJE MATEMATYCZNE
# =====================================================================

def nwd_rozszerzony(a: int, b: int):
    """Rozszerzony algorytm Euklidesa: zwraca (gcd, x, y) takie, że a*x + b*y = gcd(a, b)."""
    if a == 0:
        return b, 0, 1
    gcd, x1, y1 = nwd_rozszerzony(b % a, a)
    return gcd, y1 - (b // a) * x1, x1


def odwrotnosc_modularna(a: int, m: int) -> int:
    """Zwraca x takie, że (a * x) % m == 1; ValueError, gdy a i m nie są względnie pierwsze."""
    a %= m
    gcd, x, _ = nwd_rozszerzony(a, m)
    if gcd != 1:
        raise ValueError(f"Liczby a={a} oraz m={m} nie są względnie pierwsze! Odwrotność nie istnieje.")
    return x % m


def _sprawdz_a(a: int, m: int) -> None:
    if math.gcd(a, m) != 1:
        raise ValueError(
            f"Klucz 'a' ({a}) musi być względnie pierwszy z długością alfabetu ({m}). "
            f"NWD({a}, {m}) = {math.gcd(a, m)}."
        )


def poprawne_a(tryb: str = "ALFA26") -> list:
    """Lista wszystkich dopuszczalnych wartości klucza a (1 <= a < m, NWD(a, m) = 1)."""
    m = len(get_alphabet(tryb))
    return [a for a in range(1, m) if math.gcd(a, m) == 1]


# =====================================================================
# SZYFR AFINICZNY
# =====================================================================

def szyfruj_afiniczny(tekst: str, a: int, b: int, tryb: str = "ALFA26") -> str:
    """Szyfruje tekst: E(x) = (a*x + b) mod m.

    :param tekst: tekst jawny złożony wyłącznie ze znaków alfabetu trybu
    :param a: współczynnik mnożący, względnie pierwszy z długością alfabetu m
    :param b: współczynnik przesunięcia (dowolna liczba całkowita)
    :param tryb: 'ALFA26' lub 'ALFA37'
    """
    alfabet = get_alphabet(tryb)
    m = len(alfabet)
    _sprawdz_a(a, m)
    sprawdz_tekst(tekst, tryb)
    return "".join(alfabet[(a * alfabet.index(z) + b) % m] for z in tekst)


def deszyfruj_afiniczny(tekst_zaszyfrowany: str, a: int, b: int, tryb: str = "ALFA26") -> str:
    """Deszyfruje tekst: D(y) = a^-1 * (y - b) mod m."""
    alfabet = get_alphabet(tryb)
    m = len(alfabet)
    _sprawdz_a(a, m)
    sprawdz_tekst(tekst_zaszyfrowany, tryb)
    a_inv = odwrotnosc_modularna(a, m)
    return "".join(alfabet[(a_inv * (alfabet.index(z) - b)) % m] for z in tekst_zaszyfrowany)
