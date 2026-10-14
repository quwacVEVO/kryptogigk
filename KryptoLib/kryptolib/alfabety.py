"""Alfabety KryptoLib - jedno źródło prawdy dla wszystkich modułów.

ALFA26: A-Z (26 znaków)
ALFA37: A-Z, 0-9 i spacja (37 znaków, w tej kolejności)
"""

import string

ALFA26 = string.ascii_uppercase
ALFA37 = string.ascii_uppercase + string.digits + " "

ALFABETY = {"ALFA26": ALFA26, "ALFA37": ALFA37}

# Nazwy używane wcześniej w zadanie_2.py (zgodność wsteczna)
ALFABET_26 = ALFA26
ALFABET_37 = ALFA37


def get_alphabet(mode: str = "ALFA26") -> str:
    """Zwraca alfabet dla trybu 'ALFA26' lub 'ALFA37' (wielkość liter nie ma znaczenia)."""
    try:
        return ALFABETY[mode.upper()]
    except (KeyError, AttributeError):
        raise ValueError(f"Nieznany tryb '{mode}'. Dostępne: {list(ALFABETY)}") from None


def sprawdz_tekst(tekst: str, mode: str = "ALFA26") -> None:
    """Rzuca ValueError, jeśli tekst zawiera znak spoza alfabetu trybu.

    Szyfry nie czyszczą tekstu po cichu - przygotowanie danych to zadanie
    modułu `preprocessing` (np. przygotuj_tekst).
    """
    alfabet = set(get_alphabet(mode))
    for i, znak in enumerate(tekst):
        if znak not in alfabet:
            raise ValueError(
                f"Znak {znak!r} (pozycja {i}) nie należy do alfabetu {mode.upper()}. "
                "Tekst należy wcześniej przetworzyć modułem preprocessing."
            )
