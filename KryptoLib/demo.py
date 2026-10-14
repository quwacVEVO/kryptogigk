"""Demo KryptoLib - podpunkt 3: czytelne pokazanie szyfrowania i deszyfrowania."""

import random

from kryptolib.alfabety import get_alphabet
from kryptolib.klucze import (
    GADERYPOLUKI_FRAZY, affine_key, atbash_key, caesar_key,
    gaderypoluki_key, rot13_key,
)
from kryptolib.monoalfabetyczny import decrypt, encrypt

# Tekst jawny dla każdego trybu (musi składać się tylko ze znaków alfabetu trybu)
TEKSTY = {
    "ALFA26": "ALAMAKOTA",
    "ALFA37": "ALA MA KOTA 123",
}


def losowy_klucz(mode, seed=1):
    znaki = list(get_alphabet(mode))
    random.Random(seed).shuffle(znaki)
    return "".join(znaki)


def pokaz(nazwa, mode, tekst, klucz):
    alfabet = get_alphabet(mode)
    kryptogram = encrypt(tekst, klucz, mode)
    odszyfrowany = decrypt(kryptogram, klucz, mode)
    print(f"Szyfr:          {nazwa}")
    print(f"Tryb:           {mode}")
    print(f"Alfabet jawny:  {alfabet!r}")
    print(f"Klucz:          {klucz!r}")
    print(f"--- SZYFROWANIE ---")
    print(f"Tekst jawny:    {tekst!r}")
    print(f"Kryptogram:     {kryptogram!r}")
    print(f"--- DESZYFROWANIE ---")
    print(f"Kryptogram:     {kryptogram!r}")
    print(f"Tekst jawny:    {odszyfrowany!r}")
    print(f"Zgodność z oryginałem: {'TAK' if odszyfrowany == tekst else 'NIE !!!'}")
    print("=" * 70)


def main():
    for mode in ("ALFA26", "ALFA37"):
        tekst = TEKSTY[mode]
        szyfry = [
            ("Cezar, przesunięcie 3", caesar_key(3, mode)),
            ("Atbasz", atbash_key(mode)),
            ("ROT13", rot13_key(mode)),
        ]
        for nazwa, fraza in GADERYPOLUKI_FRAZY.items():
            szyfry.append((f"Gaderypoluki ({fraza})", gaderypoluki_key(fraza, mode)))
        szyfry.append(("Afiniczny a=5, b=8 (jako klucz permutacyjny)", affine_key(5, 8, mode)))
        szyfry.append(("Monoalfabetyczny, klucz losowy", losowy_klucz(mode)))

        for nazwa, klucz in szyfry:
            pokaz(nazwa, mode, tekst, klucz)

    # Odszyfrowanie gotowego kryptogramu podanego "z zewnątrz"
    kryptogram = "DODPDNRWD"
    klucz = caesar_key(3, "ALFA26")
    print("Przykład: samo deszyfrowanie gotowego kryptogramu")
    print(f"Szyfr:          Cezar, przesunięcie 3 (ALFA26)")
    print(f"Klucz:          {klucz!r}")
    print(f"Kryptogram:     {kryptogram!r}")
    print(f"Tekst jawny:    {decrypt(kryptogram, klucz, 'ALFA26')!r}")


if __name__ == "__main__":
    main()
    input("Naciśnij Enter, aby zamknąć okno...")
