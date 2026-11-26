import os, tempfile
from lfsr import *

liczba = 0


def ok(warunek, opis):
    """Pojedyncza kontrola: wypisuje wynik i przerywa program przy błędzie."""
    global liczba
    liczba += 1
    print(("OK   " if warunek else "BŁĄD ") + opis)
    assert warunek, opis


def wyjatek(f, *arg):
    """True, gdy wywołanie f(*arg) zgłasza ValueError (oczekiwane dla błędnych danych)."""
    try:
        f(*arg)
    except ValueError:
        return True
    return False


def bity_ref(n, tapy, ziarno, ile):
    """Niezależna implementacja wzorcowa na liście bitów (a nie na liczbie całkowitej)."""
    rej, wyjscie = [int(c) for c in format(ziarno, f"0{n}b")], []
    for _ in range(ile):
        wyjscie.append(rej[-1])
        nowy = 0
        for t in tapy:
            nowy ^= rej[t - 1]
        rej = [nowy] + rej[:-1]
    return wyjscie


def bity(n, tapy, ziarno, ile):
    """Te same bity z implementacji testowanej (krok z lfsr.py)."""
    stan, wyjscie = ziarno, []
    for _ in range(ile):
        wyjscie.append(stan & 1)
        stan = krok(stan, n, tapy)
    return wyjscie


for n, tapy, z in [(4, [4, 3], 1), (8, TAPY[8], 0xA5), (10, TAPY[10], 77), (16, TAPY[16], 0xACE1), (7, [7, 3], 5)]:
    ok(bity(n, tapy, z, 3 * 2 ** n) == bity_ref(n, tapy, z, 3 * 2 ** n), f"zgodność z wzorcem n={n} tapy={tapy}")


for n in range(3, 21):
    ok(okres(n, TAPY[n], 1) == 2 ** n - 1, f"okres maksymalny n={n}")
for n in (5, 10, 16):
    ok(sum(bity(n, TAPY[n], 1, 2 ** n - 1)) == 2 ** (n - 1), f"jedynek w okresie = 2^(n-1), n={n}")


for K, a, b in [(100, 1, 10), (50, -5, 5), (20, 7, 7), (1000, 0, 10 ** 6), (30, 1, 2)]:
    c = generuj(K, a, b, 16, TAPY[16], 0xACE1)
    ok(len(c) == K and all(a <= x <= b for x in c), f"generuj K={K} a={a} b={b}: długość i zakres")


ok(generuj(50, 0, 99, 16, TAPY[16], 5) == generuj(50, 0, 99, 16, TAPY[16], 5), "to samo ziarno daje ten sam ciąg")
ok(generuj(50, 0, 99, 16, TAPY[16], 5) != generuj(50, 0, 99, 16, TAPY[16], 6), "inne ziarno daje inny ciąg")
p = 2 ** 10 - 1
s1, s2 = bity(10, TAPY[10], 1, 2 * p), bity(10, TAPY[10], 77, p)
ok(any(s1[i:i + p] == s2 for i in range(p)), "ciąg dla innego ziarna jest przesunięciem cyklicznym (n=10)")


for n, w in [(8, 3), (8, 5), (10, 4), (12, 10), (9, 7)]:
    stan, widziane, k = 1, {}, 0
    while stan not in widziane:
        widziane[stan] = k
        for _ in range(w):
            stan = krok(stan, n, TAPY[n])
        k += 1
    ok(k == cykl_liczb(n, TAPY[n], 1, w), f"długość cyklu liczb n={n} w={w}: {k}")


for K, a, b in [(1000, 1, 100000), (100, 0, 200), (65535, 1, 65536)]:
    c, par = bez_kolizji(K, a, b)
    ok(kolizje(c) == 0 and len(c) == K and all(a <= x <= b for x in c), f"bez_kolizji K={K} [{a},{b}] n={par['n']}")
ok(wyjatek(bez_kolizji, 1000, 1, 100), "bez_kolizji: błąd, gdy K większe niż liczba wartości")


c = generuj(100, 1, 1000, 16, TAPY[16], 1)
with tempfile.TemporaryDirectory() as d:
    f = os.path.join(d, "ciag.txt")
    zapisz(f, c)
    ok(wczytaj(f) == c, "zapis i odczyt pliku zachowuje ciąg")
    ok(wyjatek(wczytaj, os.path.join(d, "nie_ma.txt")), "brak pliku zgłasza błąd")
    open(f, "w").write("12\nabc\n7\n")
    ok(wyjatek(wczytaj, f), "zły format danych zgłasza błąd")


for n, t, z in [(1, [1], 1), (65, [65], 1), ("8", [8], 1), (8, [], 1), (8, [7, 6], 1), (8, [8, 9], 1), (8, [8, 0], 1),
                (8, TAPY[8], 0), (8, TAPY[8], 256), (8, TAPY[8], 1.5)]:
    ok(wyjatek(sprawdz, n, t, z), f"błędne parametry odrzucone: n={n!r} tapy={t} ziarno={z!r}")
for K, a, b in [(0, 1, 5), (5, 9, 1)]:
    ok(wyjatek(generuj, K, a, b, 8, TAPY[8], 1), f"błędne K/zakres odrzucone: K={K} a={a} b={b}")


c = generuj(20000, 0, 9, 16, TAPY[16], 0xACE1)
chi = sum((c.count(v) - 2000) ** 2 / 2000 for v in range(10))
ok(chi < 21.67, f"równomierność wartości 0..9: chi2 = {chi:.2f} (< 21.67)")

print(f"\nWszystkie testy OK: {liczba}")
