import json
import os
import string
from Funkcje.zliczanie import *

def zapisz_json(sciezka: str, dane: dict):
    os.makedirs(os.path.dirname(sciezka), exist_ok=True)
    posortowane = dict(sorted(dane.items(), key=lambda x: (x[1], x[0]), reverse=True))
    with open(sciezka, "w", encoding="utf-8") as f:
        json.dump(posortowane, f, ensure_ascii=False, indent=4)

def wczytaj_json(sciezka: str) -> dict:
    with open(sciezka, "r", encoding="utf-8") as f:
        return json.load(f)

def oblicz_statystyki(text: str, mode: str = "alfa26"):
    folder = "Statystyki tekstu wejściowego/"

    if mode == "alfa26":
        zapisz_json(f"{folder}/alfa26_unigramy.json", przelicz_na_procenty(licz_pojedyncze_znaki(text)))
        zapisz_json(f"{folder}/alfa26_bigramy.json", przelicz_na_procenty(licz_ngramy(text, n=2)))
        zapisz_json(f"{folder}/alfa26_trigramy.json", przelicz_na_procenty(licz_ngramy(text, n=3)))

    elif mode == "alfa37":
        zapisz_json(f"{folder}/alfa37_unigramy.json", przelicz_na_procenty(licz_pojedyncze_znaki(text)))
        zapisz_json(f"{folder}/alfa37_bigramy.json", przelicz_na_procenty(licz_ngramy(text, n=2)))
        zapisz_json(f"{folder}/alfa37_trigramy.json", przelicz_na_procenty(licz_ngramy(text, n=3)))
        zapisz_json(f"{folder}/alfa37_poczatki_slow.json", przelicz_na_procenty(analizuj_poczatki_slow(text)))
        zapisz_json(f"{folder}/alfa37_konce_slow.json", przelicz_na_procenty(analizuj_konce_slow(text)))

    else: raise ValueError(f"Mode musi wynosić alfa26 lub alfa37.")

def roznica_kwadratowa(sciezka1: str, sciezka2: str):
    a = wczytaj_json(sciezka1)
    b = wczytaj_json(sciezka2)

    wszystkie_klucze = a.keys() | b.keys()
    return sum((a.get(k, 0) - b.get(k, 0)) ** 2 for k in wszystkie_klucze)

def wykryj_alfabet(text: str):
    ''' Uwaga! Zakładamy, że alfabety alfa26 i alfa37 używają wyłącznie wielkich liter.'''
    znaki = string.ascii_uppercase + " " + string.digits
    slownik = dict.fromkeys(znaki, 0)

    for znak in text:
        if znak in znaki:
            slownik[znak] += 1
        else: raise ValueError("Tekst nie wystepuje ani w alfabecie ALFA26, ani ALFA37!")

    znaki_alfa37 = " " + string.digits
    for znak in znaki_alfa37:
        if slownik[znak] != 0: return "alfa37"
    return "alfa26"

def wykryj_jezyk(text: str, mode: str = "alfa26"): 
    folder1 = "Statystyki tekstu wejściowego"
    folder2 = "Statystyki częstości występowania/Język angielski"
    folder3 = "Statystyki częstości występowania/Język polski"

    if mode == "alfa26":
        oblicz_statystyki(text, mode)

        # PORÓWNANIE Z ANGIELSKIM
        # unigramy
        sciezka1 = f"{folder1}/alfa26_unigramy.json"
        sciezka2 = f"{folder2}/alfa26_unigramy.json"
        suma_unigramy = roznica_kwadratowa(sciezka1, sciezka2)
        #bigramy
        sciezka1 = f"{folder1}/alfa26_bigramy.json"
        sciezka2 = f"{folder2}/alfa26_bigramy.json"
        suma_bigramy = roznica_kwadratowa(sciezka1, sciezka2)
        #trigramy
        sciezka1 = f"{folder1}/alfa26_trigramy.json"
        sciezka2 = f"{folder2}/alfa26_trigramy.json"
        suma_trigramy = roznica_kwadratowa(sciezka1, sciezka2)

        suma_ang = suma_unigramy + suma_bigramy + suma_trigramy

        # PORÓWNANIE Z POLSKIM
        # unigramy
        sciezka1 = f"{folder1}/alfa26_unigramy.json"
        sciezka2 = f"{folder3}/alfa26_unigramy.json"
        suma_unigramy = roznica_kwadratowa(sciezka1, sciezka2)
        #bigramy
        sciezka1 = f"{folder1}/alfa26_bigramy.json"
        sciezka2 = f"{folder3}/alfa26_bigramy.json"
        suma_bigramy = roznica_kwadratowa(sciezka1, sciezka2)
        #trigramy
        sciezka1 = f"{folder1}/alfa26_trigramy.json"
        sciezka2 = f"{folder3}/alfa26_trigramy.json"
        suma_trigramy = roznica_kwadratowa(sciezka1, sciezka2)

        suma_pl = suma_unigramy + suma_bigramy + suma_trigramy

        if (suma_ang < suma_pl): return "angielski"
        else: return "polski"

    elif mode == "alfa37":
        oblicz_statystyki(text, mode)

        # PORÓWNANIE Z ANGIELSKIM
        # unigramy
        sciezka1 = f"{folder1}/alfa37_unigramy.json"
        sciezka2 = f"{folder2}/alfa37_unigramy.json"
        suma_unigramy = roznica_kwadratowa(sciezka1, sciezka2)
        #bigramy
        sciezka1 = f"{folder1}/alfa37_bigramy.json"
        sciezka2 = f"{folder2}/alfa37_bigramy.json"
        suma_bigramy = roznica_kwadratowa(sciezka1, sciezka2)
        #trigramy
        sciezka1 = f"{folder1}/alfa37_trigramy.json"
        sciezka2 = f"{folder2}/alfa37_trigramy.json"
        suma_trigramy = roznica_kwadratowa(sciezka1, sciezka2)
        #początki słów
        sciezka1 = f"{folder1}/alfa37_poczatki_slow.json"
        sciezka2 = f"{folder2}/alfa37_poczatki_slow.json"
        suma_poczatki_slow = roznica_kwadratowa(sciezka1, sciezka2)
        #końce słów
        sciezka1 = f"{folder1}/alfa37_konce_slow.json"
        sciezka2 = f"{folder2}/alfa37_konce_slow.json"
        suma_konce_slow = roznica_kwadratowa(sciezka1, sciezka2)

        suma_ang = suma_unigramy + suma_bigramy + suma_trigramy + suma_poczatki_slow + suma_konce_slow

        # PORÓWNANIE Z POLSKIM
        # unigramy
        sciezka1 = f"{folder1}/alfa37_unigramy.json"
        sciezka2 = f"{folder3}/alfa37_unigramy.json"
        suma_unigramy = roznica_kwadratowa(sciezka1, sciezka2)
        #bigramy
        sciezka1 = f"{folder1}/alfa37_bigramy.json"
        sciezka2 = f"{folder3}/alfa37_bigramy.json"
        suma_bigramy = roznica_kwadratowa(sciezka1, sciezka2)
        #trigramy
        sciezka1 = f"{folder1}/alfa37_trigramy.json"
        sciezka2 = f"{folder3}/alfa37_trigramy.json"
        suma_trigramy = roznica_kwadratowa(sciezka1, sciezka2)
        #początki słów
        sciezka1 = f"{folder1}/alfa37_poczatki_slow.json"
        sciezka2 = f"{folder3}/alfa37_poczatki_slow.json"
        suma_poczatki_slow = roznica_kwadratowa(sciezka1, sciezka2)
        #końce słów
        sciezka1 = f"{folder1}/alfa37_konce_slow.json"
        sciezka2 = f"{folder3}/alfa37_konce_slow.json"
        suma_konce_slow = roznica_kwadratowa(sciezka1, sciezka2)

        suma_pl = suma_unigramy + suma_bigramy + suma_trigramy + suma_poczatki_slow + suma_konce_slow

        print(suma_ang)
        print(suma_pl)

        if (suma_ang < suma_pl): return "angielski"
        else: return "polski"
    
    else: raise ValueError(f"Mode musi wynosić alfa26 lub alfa37.")


