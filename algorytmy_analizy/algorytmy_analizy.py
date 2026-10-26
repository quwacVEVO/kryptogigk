"""
Algorytmy analizy i dane statystyczne.
"""

import sys
import os
import json
from collections import Counter
from pathlib import Path

# Dodanie katalogu nadrzędnego do ścieżki systemowej, aby zaimportować kryptolib
sys.path.append(str(Path(__file__).resolve().parent.parent))

ALFA26 = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
ALFA37 = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 "

dozwolone_znaki = set(ALFA26)

BASE_DIR = Path(__file__).resolve().parent
folder_pl = BASE_DIR / "Statystyki częstości występowania" / "Język polski"
folder_eng = BASE_DIR / "Statystyki częstości występowania" / "Język angielski"

if not folder_pl.exists():
    folder_pl = BASE_DIR.parent / "Statystyki częstości występowania" / "Język polski"
    folder_eng = BASE_DIR.parent / "Statystyki częstości występowania" / "Język angielski"

with open(folder_pl / "alfa26_unigramy.json", "r", encoding="utf-8") as f:
    unipl = json.load(f)
with open(folder_pl / "alfa26_bigramy.json", "r", encoding="utf-8") as f:
    bipl = json.load(f)
with open(folder_pl / "alfa26_trigramy.json", "r", encoding="utf-8") as f:
    tripl = json.load(f)

with open(folder_eng / "alfa26_unigramy.json", "r", encoding="utf-8") as f:
    unieng = json.load(f)
with open(folder_eng / "alfa26_bigramy.json", "r", encoding="utf-8") as f:
    bieng = json.load(f)
with open(folder_eng / "alfa26_trigramy.json", "r", encoding="utf-8") as f:
    trieng = json.load(f)

REF_FREQS = {
    "polski": unipl,
    "angielski": unieng
}

REF_BIGRAMS = {
    "polski": bipl,
    "angielski": bieng
}

REF_TRIGRAMS = {
    "polski": tripl,
    "angielski": trieng
}

REF_IOC = {
    "polski": 0.0610,
    "angielski": 0.0667
}


def oblicz_statystyki(text: str, mode: str = "alfa26"):
    if mode == "alfa26":
        unigramy = przelicz_na_procenty(licz_pojedyncze_znaki(text))
        bigramy = przelicz_na_procenty(licz_ngramy(text, n=2))
        trigramy = przelicz_na_procenty(licz_ngramy(text, n=3))

        unigramy_sortowane = dict(sorted(unigramy.items(), key=lambda x: (x[1], x[0]), reverse=True))
        bigramy_sortowane = dict(sorted(bigramy.items(), key=lambda x: (x[1], x[0]), reverse=True))
        trigramy_sortowane = dict(sorted(trigramy.items(), key=lambda x: (x[1], x[0]), reverse=True))
        
        ngramy_sortowane = {
            "unigramy": unigramy_sortowane,
            "bigramy": bigramy_sortowane,
            "trigramy": trigramy_sortowane
        }
        return ngramy_sortowane

    elif mode == "alfa37":
        raise ValueError("Mode musi wynosić alfa26 bo alfa37 nie działa.")
    else:
        raise ValueError("Mode musi wynosić alfa26 lub alfa37.")


def licz_pojedyncze_znaki(tekst):
    licznik = {}
    for znak in tekst:
        if znak not in dozwolone_znaki:
            continue
        licznik[znak] = licznik.get(znak, 0) + 1
    return licznik


def licz_ngramy(tekst, n):
    licznik = {}
    for i in range(len(tekst) - n + 1):
        fragment = tekst[i: i + n]
        if not set(fragment) <= dozwolone_znaki:
            continue
        licznik[fragment] = licznik.get(fragment, 0) + 1
    return licznik


def przelicz_na_procenty(licznik_wystapien):
    suma_wszystkich = sum(licznik_wystapien.values())
    if suma_wszystkich == 0:
        return {}
    procenty = {}
    for klucz, ilosc in licznik_wystapien.items():
        procenty[klucz] = (ilosc / suma_wszystkich) * 100
    return procenty


def calculate_ioc(text: str, alphabet_len: int = 26) -> float:
    upper_text = text.upper()
    n = len(upper_text)
    if n <= 1:
        return 0.0
    counts = Counter(upper_text)
    sum_fi = sum(f * (f - 1) for f in counts.values())
    return sum_fi / (n * (n - 1))