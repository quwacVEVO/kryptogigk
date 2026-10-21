import string

dozwolone_znaki = set(string.ascii_uppercase + string.digits + " ")

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

def analizuj_poczatki_slow(tekst, separator=" ", dlugosc_zbitek = 2):
    licznik = {}
    slowa = tekst.split(separator)

    for slowo in slowa:
        if len(slowo) >= dlugosc_zbitek:
            poczatek = slowo[:dlugosc_zbitek]

            if not set(poczatek) <= dozwolone_znaki:
                continue
            licznik[poczatek] = licznik.get(poczatek, 0) + 1

    return licznik

def analizuj_konce_slow(tekst, separator=" ", dlugosc_zbitek = 2):
    licznik = {}
    for slowo in tekst.split(separator):
        if len(slowo) >= dlugosc_zbitek:
            koniec = slowo[-dlugosc_zbitek:]

            if not set(koniec) <= dozwolone_znaki:
                continue
            licznik[koniec] = licznik.get(koniec, 0) + 1

    return licznik

def przelicz_na_procenty(licznik_wystapien):
    suma_wszystkich = sum(licznik_wystapien.values())
    procenty = {}

    for klucz, ilosc in licznik_wystapien.items():
        procenty[klucz] = (ilosc / suma_wszystkich) * 100

    return procenty