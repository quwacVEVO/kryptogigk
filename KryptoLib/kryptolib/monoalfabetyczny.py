"""Uogólniony szyfr monoalfabetyczny (ALFA26 / ALFA37) z kluczem permutacyjnym.

Szyfry Cezara, Atbasz, ROT13 i Gaderypoluki to szczególne przypadki:
różnią się wyłącznie kluczem (patrz moduł `klucze`), a szyfrowanie
wykonuje zawsze to samo `encrypt` / `decrypt`.
"""

from .alfabety import ALFA26, ALFA37, get_alphabet, sprawdz_tekst
from .klucze import (  # noqa: F401  (re-eksport dla wygody)
    GADERYPOLUKI_FRAZY, affine_key, atbash_key, caesar_key,
    gaderypoluki_key, rot13_key,
)


# ---------------------------------------------------------------------------
# Klucz permutacyjny
# ---------------------------------------------------------------------------
def validate_key(key: str, mode: str = "ALFA26") -> None:
    """Sprawdza, czy klucz jest poprawną permutacją alfabetu danego trybu.

    Rzuca ValueError przy złej długości, powtórzeniach lub znakach spoza alfabetu.
    """
    alphabet = get_alphabet(mode)
    if len(key) != len(alphabet):
        raise ValueError(
            f"Klucz dla {mode.upper()} musi mieć {len(alphabet)} znaków, a ma {len(key)}."
        )
    if len(set(key)) != len(key):
        dup = sorted({c for c in key if key.count(c) > 1})
        raise ValueError(f"Klucz zawiera powtórzone znaki: {dup}")
    if set(key) != set(alphabet):
        obce = sorted(set(key) - set(alphabet))
        raise ValueError(f"Klucz zawiera znaki spoza alfabetu {mode.upper()}: {obce}")


def invert_key(key: str, mode: str = "ALFA26") -> str:
    """Zwraca klucz odwrotny (do deszyfrowania)."""
    validate_key(key, mode)
    alphabet = get_alphabet(mode)
    inv = [""] * len(alphabet)
    for plain, cipher in zip(alphabet, key):
        inv[alphabet.index(cipher)] = plain
    return "".join(inv)


# ---------------------------------------------------------------------------
# Szyfr ogólny
# ---------------------------------------------------------------------------
def _substitute(text: str, source: str, target: str) -> str:
    table = dict(zip(source, target))
    return "".join(table[c] for c in text)


def encrypt(text: str, key: str, mode: str = "ALFA26") -> str:
    """Szyfruje tekst: znak alfabetu na pozycji i zastępowany jest znakiem key[i]."""
    validate_key(key, mode)
    sprawdz_tekst(text, mode)
    return _substitute(text, get_alphabet(mode), key)


def decrypt(text: str, key: str, mode: str = "ALFA26") -> str:
    """Deszyfruje tekst zaszyfrowany funkcją encrypt tym samym kluczem."""
    validate_key(key, mode)
    sprawdz_tekst(text, mode)
    return _substitute(text, key, get_alphabet(mode))


# ---------------------------------------------------------------------------
# Szyfry szczególne wykonywane szyfrem ogólnym
# ---------------------------------------------------------------------------
def caesar_encrypt(text, shift, mode="ALFA26"):
    return encrypt(text, caesar_key(shift, mode), mode)


def caesar_decrypt(text, shift, mode="ALFA26"):
    return decrypt(text, caesar_key(shift, mode), mode)


def atbash_encrypt(text, mode="ALFA26"):
    return encrypt(text, atbash_key(mode), mode)


def atbash_decrypt(text, mode="ALFA26"):
    return decrypt(text, atbash_key(mode), mode)


def rot13_encrypt(text, mode="ALFA26"):
    return encrypt(text, rot13_key(mode), mode)


def rot13_decrypt(text, mode="ALFA26"):
    return decrypt(text, rot13_key(mode), mode)


def gaderypoluki_encrypt(text, phrase="GADERYPOLUKI", mode="ALFA26"):
    return encrypt(text, gaderypoluki_key(phrase, mode), mode)


def gaderypoluki_decrypt(text, phrase="GADERYPOLUKI", mode="ALFA26"):
    return decrypt(text, gaderypoluki_key(phrase, mode), mode)
