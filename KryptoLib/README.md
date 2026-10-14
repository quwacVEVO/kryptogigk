# KryptoLib 1.0 (Grupa 4, GenAI)

Biblioteka klasycznych szyfrów podstawieniowych w Pythonie (tryby ALFA26 i ALFA37).

## Struktura
```
kryptolib/
    alfabety.py          alfabety ALFA26 / ALFA37 (jedno źródło prawdy)
    preprocessing.py     część 1: czyszczenie, formatowanie, kolumny, pliki, tryby ALFA26/ALFA37
    klucze.py            klucze: Cezar, Atbasz, ROT13, Gaderypoluki, afiniczny (26 i 37 znaków)
    afiniczny.py         część 2: szyfr afiniczny
    monoalfabetyczny.py  część 3: uogólniony szyfr monoalfabetyczny + szyfry szczególne
demo.py                  krótkie demo: szyfr, klucz, tekst jawny, kryptogram, deszyfrowanie
demo_rozszerzony.py      pełna demonstracja wszystkich funkcji (107 sprawdzeń)
test_*.py                testy jednostkowe (unittest, bez dodatkowych pakietów)
```

## Zasady spójności
- Szyfry NIE czyszczą tekstu po cichu: znak spoza alfabetu = `ValueError`.
  Tekst przygotowuje się wcześniej: `preprocessing.przygotuj_tekst(tekst, "ALFA26")`.
- Cezar, Atbasz, ROT13, Gaderypoluki i afiniczny to klucze permutacyjne (`klucze.py`),
  a szyfrowanie wykonuje szyfr ogólny: `monoalfabetyczny.encrypt(tekst, klucz, tryb)`.
- ALFA37 = A-Z, 0-9, spacja (w tej kolejności).

## Uruchamianie
```
python demo.py
python demo_rozszerzony.py
python -m unittest discover -v
```
