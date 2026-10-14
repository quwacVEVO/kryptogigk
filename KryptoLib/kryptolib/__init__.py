"""KryptoLib 1.0 - podstawowa biblioteka klasycznych szyfrów podstawieniowych.

Moduły:
    alfabety           - alfabety ALFA26 / ALFA37
    preprocessing      - czyszczenie i standaryzacja tekstu, kolumny, pliki
    klucze             - klucze: Cezar, Atbasz, ROT13, Gaderypoluki, afiniczny
    monoalfabetyczny   - uogólniony szyfr monoalfabetyczny (klucz permutacyjny)
    afiniczny          - szyfr afiniczny
"""

from . import afiniczny, alfabety, klucze, monoalfabetyczny, preprocessing
from .afiniczny import deszyfruj_afiniczny, szyfruj_afiniczny
from .alfabety import ALFA26, ALFA37, get_alphabet
from .monoalfabetyczny import decrypt, encrypt, invert_key, validate_key
from .preprocessing import przygotuj_tekst, tryb_alfa26, tryb_alfa37

__version__ = "1.0"
