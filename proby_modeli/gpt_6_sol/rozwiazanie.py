"""Dwa sposoby liczenia logarytmu dyskretnego w ciele Z/pZ."""

from math import isqrt
from time import perf_counter_ns

from sympy import factorint, isprime
from sympy.ntheory.modular import crt


ZADANIA = [
    ("Z1", 37781, 3, 24581),
    ("Z2", 100000127, 5, 5910514),
    ("Z3", 1000000000547, 2, 514634099897),
    ("Z4", 33815155531460793491, 19, 30073559734842340154),
]
LIMIT_TABLICY = 2_000_000


def sufit_pierwiastka(n):
    """Dokładny całkowity sufit pierwiastka, bez liczb zmiennoprzecinkowych."""
    m = isqrt(n)
    return m if m * m == n else m + 1


def rzad_elementu(g, p):
    """Zmniejszamy p-1, testując kolejne dzielniki pierwsze."""
    n = p - 1
    for q in factorint(n):
        while n % q == 0 and pow(g, n // q, p) == 1:
            n //= q
    return n


def bsgs(g, h, p, n):
    """Baby-step giant-step: O(sqrt(n)) czasu i pamięci."""
    m = sufit_pierwiastka(n)
    male = {}
    wartosc = 1
    for j in range(m):
        male.setdefault(wartosc, j)
        wartosc = wartosc * g % p

    skok = pow(pow(g, m, p), -1, p)
    wartosc = h
    for i in range(m + 1):
        if wartosc in male:
            a = i * m + male[wartosc]
            if a < n and pow(g, a, p) == h:
                return a
        wartosc = wartosc * skok % p
    return None


def pohlig_hellman(g, h, p, n):
    """Liczymy cyfry logarytmu modulo q^e, następnie składamy wyniki CRT."""
    moduly = []
    reszty = []
    for q, e in factorint(n).items():
        q = int(q)
        e = int(e)
        baza = pow(g, n // q, p)  # element rzędu q
        x = 0
        for j in range(e):
            korekta = h * pow(pow(g, x, p), -1, p) % p
            cel = pow(korekta, n // (q ** (j + 1)), p)
            cyfra = bsgs(baza, cel, p, q)
            if cyfra is None:
                return None
            x += cyfra * q**j
        moduly.append(q**e)
        reszty.append(x)
    wynik, _ = crt(moduly, reszty)
    a = int(wynik) % n
    return a if pow(g, a, p) == h else None


def uruchom():
    print("Metody: BSGS oraz Pohlig–Hellman; sekundy mierzone perf_counter_ns.", flush=True)
    for nazwa, p, g, h in ZADANIA:
        assert isprime(p), f"{nazwa}: p nie jest pierwsze"
        n = rzad_elementu(g, p)
        m = sufit_pierwiastka(n)
        print(f"{nazwa}: p={p}, g={g}, h={h}, rząd(g)={n}, czynniki={factorint(n)}", flush=True)
        if m > LIMIT_TABLICY:
            print(
                f"  BSGS: pominięto; szacunkowo {m:,} wpisów tablicy "
                f"i do {m + 1:,} dużych kroków (bez oszacowania czasu).",
                flush=True,
            )
        else:
            start = perf_counter_ns()
            a = bsgs(g, h, p, n)
            czas_ns = perf_counter_ns() - start
            print(
                f"  BSGS: a={a}, weryfikacja={a is not None and pow(g, a, p) == h}, "
                f"czas_ns={czas_ns}, czas_s={czas_ns / 1e9:.9f}",
                flush=True,
            )
            assert a is not None and pow(g, a, p) == h

        # Dla tych danych największy czynnik pierwszy rzędu jest mały na tyle,
        # że wszystkie wewnętrzne wywołania BSGS mieszczą się w limicie.
        najwiekszy = max(factorint(n))
        if sufit_pierwiastka(int(najwiekszy)) > LIMIT_TABLICY:
            print("  Pohlig–Hellman: pominięto przez limit tablicy.", flush=True)
            continue
        start = perf_counter_ns()
        a = pohlig_hellman(g, h, p, n)
        czas_ns = perf_counter_ns() - start
        print(
            f"  Pohlig–Hellman: a={a}, weryfikacja={a is not None and pow(g, a, p) == h}, "
            f"czas_ns={czas_ns}, czas_s={czas_ns / 1e9:.9f}",
            flush=True,
        )
        assert a is not None and pow(g, a, p) == h


if __name__ == "__main__":
    uruchom()
