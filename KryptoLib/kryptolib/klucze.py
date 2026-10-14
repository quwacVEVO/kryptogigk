"""Generatory kluczy permutacyjnych (26- lub 37-znakowych) dla szyfrów
podstawieniowych: Cezar, Atbasz, ROT13, Gaderypoluki oraz szyfr afiniczny.

Każdy klucz to permutacja alfabetu trybu: znak alfabetu na pozycji i jest
zastępowany znakiem klucza z pozycji i. Dzięki temu wszystkie te szyfry
można wykonać szyfrem ogólnym (monoalfabetyczny.encrypt / decrypt).
"""

import math

from .alfabety import ALFA26, get_alphabet

# Przykładowe klucze Gaderypoluki (min. 3 wymagane w zadaniu)
GADERYPOLUKI_FRAZY = {
    "GADERYPOLUKI": "GADERYPOLUKI",
    "POLITYKARENU": "POLITYKARENU",
    "KACEMINUTOWY": "KACEMINUTOWY",
    "MOTYLEBAKUSI": "MOTYLEBAKUSI",
}


def caesar_key(shift: int, mode: str = "ALFA26") -> str:
    """Klucz Cezara: cykliczne przesunięcie całego alfabetu o `shift` (modulo długość alfabetu)."""
    alphabet = get_alphabet(mode)
    s = shift % len(alphabet)
    return alphabet[s:] + alphabet[:s]


def atbash_key(mode: str = "ALFA26") -> str:
    """Klucz Atbasz: alfabet odwrócony (A<->Z, B<->Y, ...).

    W ALFA37 odwracany jest cały alfabet (A<->spacja, B<->9, ...).
    """
    return get_alphabet(mode)[::-1]


def _tylko_litery(klucz_liter: str, mode: str) -> str:
    """Rozszerza klucz 26-literowy na tryb: cyfry i spacja zostają bez zmian."""
    return klucz_liter + get_alphabet(mode)[26:]


def rot13_key(mode: str = "ALFA26") -> str:
    """Klucz ROT13 (Cezar o 13 na literach; w ALFA37 cyfry i spacja bez zmian)."""
    return _tylko_litery(caesar_key(13, "ALFA26"), mode)


def gaderypoluki_key(phrase: str = "GADERYPOLUKI", mode: str = "ALFA26") -> str:
    """Klucz Gaderypoluki z frazy złożonej z par liter, np. GA-DE-RY-PO-LU-KI.

    Litery w parze zamieniają się miejscami (G<->A, D<->E, ...), pozostałe
    litery (oraz cyfry i spacja w ALFA37) nie zmieniają się.
    Myślniki i spacje we frazie są ignorowane.
    """
    phrase = phrase.upper().replace("-", "").replace(" ", "")
    if len(phrase) % 2 != 0:
        raise ValueError("Fraza Gaderypoluki musi składać się z par liter (parzysta długość).")
    if len(set(phrase)) != len(phrase) or not set(phrase) <= set(ALFA26):
        raise ValueError("Litery frazy Gaderypoluki muszą być unikalne i należeć do A-Z.")
    mapping = {c: c for c in ALFA26}
    for a, b in zip(phrase[0::2], phrase[1::2]):
        mapping[a], mapping[b] = b, a
    return _tylko_litery("".join(mapping[c] for c in ALFA26), mode)


def affine_key(a: int, b: int, mode: str = "ALFA26") -> str:
    """Klucz szyfru afinicznego E(x) = (a*x + b) mod m jako permutacja alfabetu.

    `a` musi być względnie pierwsze z długością alfabetu m (26 lub 37).
    """
    alphabet = get_alphabet(mode)
    m = len(alphabet)
    if math.gcd(a, m) != 1:
        raise ValueError(
            f"Klucz 'a' ({a}) musi być względnie pierwszy z długością alfabetu ({m}). "
            f"NWD({a}, {m}) = {math.gcd(a, m)}."
        )
    return "".join(alphabet[(a * i + b) % m] for i in range(m))


# ---------------------------------------------------------------------------
# Nazwy polskie z zadanie_2.py (zgodność wsteczna; domyślnie ALFA26)
# ---------------------------------------------------------------------------
def klucz_cezara(przesuniecie: int, tryb: str = "ALFA26") -> str:
    return caesar_key(przesuniecie, tryb)


def klucz_atbasz(tryb: str = "ALFA26") -> str:
    return atbash_key(tryb)


def klucz_rot13(tryb: str = "ALFA26") -> str:
    return rot13_key(tryb)


def klucz_gaderypoluki(parne_slowo: str = "GADERYPOLUKI", tryb: str = "ALFA26") -> str:
    return gaderypoluki_key(parne_slowo, tryb)


def klucz_afiniczny(a: int, b: int, tryb: str = "ALFA26") -> str:
    return affine_key(a, b, tryb)
