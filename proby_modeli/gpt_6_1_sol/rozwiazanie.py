"""Logarytmy dyskretne: BSGS i Pohlig–Hellman, z rzeczywistymi pomiarami.

Wymaga pakietu sympy. Czasy obejmują obliczenia danej metody;
czas dodatkowej weryfikacji wyniku wypisujemy osobno.
"""
import json
import math
import time
from sympy import factorint, isprime

ZADANIA = [
    ('Z1', 37781, 3, 24581),
    ('Z2', 100000127, 5, 5910514),
    ('Z3', 1000000000547, 2, 514634099897),
    ('Z4', 33815155531460793491, 19, 30073559734842340154),
]
LIMIT_TABLICY = 1_100_000


def rozmiar(n):
    """Sufit z pierwiastka bez utraty dokładności dla dużych liczb."""
    return math.isqrt(n - 1) + 1


def bsgs(g, h, p, n):
    """Szuka a w [0,n), przy znanym ograniczeniu n na rząd grupy."""
    m = rozmiar(n)
    if m > LIMIT_TABLICY:
        raise RuntimeError(f'Potrzeba {m} elementów tablicy; limit {LIMIT_TABLICY}.')
    male = {}
    potega = 1
    for j in range(m):
        male.setdefault(potega, j)
        potega = potega * g % p
    krok = pow(pow(g, m, p), -1, p)
    wartosc = h % p
    for i in range((n + m - 1) // m):
        if wartosc in male:
            a = i * m + male[wartosc]
            if a < n:
                return a
        wartosc = wartosc * krok % p
    raise ValueError('Brak logarytmu w podanym zakresie.')


def pohlig_hellman(g, h, p):
    """Rozkład rzędu, cyfry logarytmu w grupach rzędu q i CRT."""
    # Limit faktoryzacji chroni przed kosztowną próbą rozkładu trudnej liczby.
    czynniki = {int(q): int(e) for q, e in factorint(p - 1, limit=1_000_000).items()}
    if not all(isprime(q) for q in czynniki):
        raise RuntimeError(f'Niepełny rozkład p-1 przy limicie faktoryzacji: {czynniki}')
    # Najpierw wyznaczamy rzeczywisty rząd g, dzielący p-1.
    n = p - 1
    for q in czynniki:
        while n % q == 0 and pow(g, n // q, p) == 1:
            n //= q
    rzad_czynniki = {}
    reszta = n
    for q in czynniki:
        e = 0
        while reszta % q == 0:
            reszta //= q
            e += 1
        if e:
            rzad_czynniki[q] = e
    if pow(h, n, p) != 1:
        raise ValueError('h nie należy do podgrupy generowanej przez g.')
    for q in rzad_czynniki:
        if rozmiar(q) > LIMIT_TABLICY:
            raise RuntimeError(f'Podproblem rzędu {q}: tablica {rozmiar(q)} przekracza limit.')
    a, modul = 0, 1
    for q, e in rzad_czynniki.items():
        gamma = pow(g, n // q, p)  # Element rzędu q.
        x = 0
        for k in range(e):
            poprawione_h = h * pow(pow(g, x, p), -1, p) % p
            cel = pow(poprawione_h, n // (q ** (k + 1)), p)
            cyfra = bsgs(gamma, cel, p, q)
            x += cyfra * q ** k
        # Łączymy a modulo modul z x modulo q**e.
        nowy_modul = q ** e
        a += modul * (((x - a) * pow(modul, -1, nowy_modul)) % nowy_modul)
        modul *= nowy_modul
        a %= modul
    return a, {'rzad_g': n, 'rozklad_p_minus_1': czynniki, 'rozklad_rzedu_g': rzad_czynniki}


def wypisz(dane):
    print(json.dumps(dane, ensure_ascii=False, sort_keys=True), flush=True)


def main():
    wypisz({'opis': 'Dwie metody: baby-step giant-step (BSGS) i Pohlig–Hellman z BSGS dla cyfr.',
            'zlozonosc': 'BSGS: O(sqrt(n)) czasu i pamięci. PH: faktoryzacja oraz O(sum(e_q * (sqrt(q) + log(n)))) operacji modularnych.',
            'uwaga': 'Czasy measured_seconds są zmierzone, a estymacje kroków są teoretyczne. PH obejmuje faktoryzację i wyznaczenie rzędu.'})
    for nazwa, p, g, h in ZADANIA:
        assert isprime(p), f'{nazwa}: moduł nie jest pierwszy'
        for metoda in ['BSGS', 'Pohlig-Hellman']:
            dane = {'zadanie': nazwa, 'p': p, 'g': g, 'h': h, 'metoda': metoda}
            m = rozmiar(p - 1)
            if metoda == 'BSGS' and m > LIMIT_TABLICY:
                dane.update({'status': 'pominieto', 'measured_seconds': None,
                             'powod': 'Zbyt duże zapotrzebowanie na czas i pamięć.',
                             'estymacja_elementow_tablicy': m,
                             'estymacja_krokow_do': m + (p - 2 + m) // m,
                             'estymacja_pamieci_samych_reszt_bajty': m * ((p.bit_length() + 7) // 8),
                             'uwaga_pamiec': 'Dolne ograniczenie na przechowanie reszt; słownik i wykładniki wymagają dodatkowej pamięci.'})
                wypisz(dane)
                continue
            start = time.perf_counter_ns()
            try:
                if metoda == 'BSGS':
                    a = bsgs(g, h, p, p - 1)
                    szczegoly = {'ograniczenie_rzedu': p - 1, 'elementy_tablicy': m}
                else:
                    a, szczegoly = pohlig_hellman(g, h, p)
                koniec = time.perf_counter_ns()
                start_weryfikacji = time.perf_counter_ns()
                sprawdzenie = pow(g, a, p) == h
                koniec_weryfikacji = time.perf_counter_ns()
                assert sprawdzenie
                dane.update({'status': 'ok', 'a': a, 'verified': sprawdzenie,
                             'measured_ns': koniec - start,
                             'measured_seconds': (koniec - start) / 1e9,
                             'verification_ns': koniec_weryfikacji - start_weryfikacji, **szczegoly})
            except (RuntimeError, ValueError) as blad:
                koniec = time.perf_counter_ns()
                dane.update({'status': 'nie_ukonczono', 'powod': str(blad),
                             'measured_ns': koniec - start, 'measured_seconds': (koniec - start) / 1e9})
            wypisz(dane)


if __name__ == '__main__':
    main()
