import json, time, statistics
from math import gcd
from lfsr import *

wyn = {}


def czas_ms(f, p=5):
    """Mediana czasu wykonania f() w milisekundach z p powtórzeń."""
    t = []
    for _ in range(p):
        t0 = time.perf_counter(); f(); t.append((time.perf_counter() - t0) * 1000)
    return statistics.median(t)


def ocz_kol(K, R):
    """Oczekiwana liczba kolizji dla K liczb losowych z R możliwych (wartość porównawcza)."""
    return K - R * (1 - (1 - 1 / R) ** K)


def chi2(c, a, b, k=16):
    """Statystyka chi-kwadrat równomierności: liczby dzielone na k równych przedziałów [a, b]."""
    ile = [0] * k
    for x in c:
        ile[(x - a) * k // (b - a + 1)] += 1
    return sum((o - len(c) / k) ** 2 / (len(c) / k) for o in ile)


def jedynki(n, tapy, z, L=100000):
    """Odsetek jedynek wśród pierwszych L bitów wyjściowych rejestru."""
    s, ile = z, 0
    for _ in range(L):
        ile += s & 1; s = krok(s, n, tapy)
    return ile / L


def okres_slownik(n, tapy, z):
    """Okres rejestru (metoda 2): zapamiętujemy wszystkie stany w słowniku do pierwszego powtórzenia."""
    widz, s, k = {}, z, 0
    while s not in widz:
        widz[s] = k; s = krok(s, n, tapy); k += 1
    return k - widz[s]


def wiersz(K, a, b, n, tapy, z):
    """Zestaw miar jakości ciągu dla jednej konfiguracji (K liczb z [a, b])."""
    w = max(1, (b - a).bit_length())
    c = generuj(K, a, b, n, tapy, z)
    p = okres(n, tapy, z)
    return dict(n=n, tapy=tapy, ziarno=z, okres=p, cykl=p // gcd(p, w), kolizje=kolizje(c), losowe=ocz_kol(K, b - a + 1),
                jedynki=jedynki(n, tapy, z), chi2=chi2(c, a, b), ms=czas_ms(lambda: generuj(K, a, b, n, tapy, z)), pierwsze=c[:5])


def tex(plik, naglowki, wiersze, spec):
    """Zapis tabeli w LaTeX (booktabs) do pliku."""
    with open(plik, "w") as f:
        f.write("\\begin{tabular}{" + spec + "}\\toprule\n" + " & ".join(naglowki) + " \\\\ \\midrule\n")
        for r in wiersze:
            f.write(" & ".join(str(x) for x in r) + " \\\\\n")
        f.write("\\bottomrule\\end{tabular}\n")


def sp(x):
    """Liczba całkowita ze spacją co trzy cyfry (czytelność w tabelach)."""
    return f"{x:,}".replace(",", "\\,")


c1 = generuj(1000, 1, 1000, 16, TAPY[16], 0xACE1)
zapisz("ciag_z_kolizjami.txt", c1)
c2, par = bez_kolizji(1000, 1, 100000)
zapisz("ciag_bez_kolizji.txt", c2)
wyn["plik_z_kolizjami"] = dict(parametry=dict(K=1000, a=1, b=1000, n=16, tapy=TAPY[16], ziarno=0xACE1),
                               kolizje=kolizje(wczytaj("ciag_z_kolizjami.txt")), losowe=ocz_kol(1000, 1000))
wyn["plik_bez_kolizji"] = dict(parametry=par, kolizje=kolizje(wczytaj("ciag_bez_kolizji.txt")))


T1 = [wiersz(1000, 0, 2 ** 20 - 1, n, TAPY[n], 0xACE1 & (2 ** n - 1)) for n in (8, 10, 12, 14, 16, 18, 20, 22, 24)]
tex("t1.tex", ["$n$", "okres", "cykl liczb", "kolizje", "losowe", "\\% jedynek", "$\\chi^2$", "czas [ms]"],
    [[r["n"], sp(r["okres"]), sp(r["cykl"]), r["kolizje"], f"{r['losowe']:.1f}", f"{100*r['jedynki']:.2f}", f"{r['chi2']:.1f}",
      f"{r['ms']:.1f}"] for r in T1], "rrrrrrrr")


tapy2 = [[16, 15, 13, 4], [16, 5, 3, 2], [16, 14, 13, 11], [16, 15], [16, 12], [16, 8], [16]]
T2 = [wiersz(2000, 1, 65536, 16, t, 0xACE1) for t in tapy2]
tex("t2.tex", ["tapy", "okres", "cykl liczb", "kolizje", "\\% jedynek", "$\\chi^2$"],
    [["$" + str(r["tapy"]).replace(" ", "") + "$", sp(r["okres"]), sp(r["cykl"]), r["kolizje"], f"{100*r['jedynki']:.2f}", f"{r['chi2']:.1f}"]
     for r in T2], "lrrrrr")


T3a = [wiersz(1000, 1, 65536, 16, TAPY[16], z) for z in (1, 2, 0xACE1, 0xFFFF, 0x8000)]
tex("t3a.tex", ["ziarno", "okres", "kolizje", "pierwsze 3 liczby"],
    [[r["ziarno"], sp(r["okres"]), r["kolizje"], ",\\,".join(map(str, r["pierwsze"][:3]))] for r in T3a], "rrrl")
T3b = [wiersz(1000, 1, 65536, 16, [16, 11, 1], z) for z in (1, 2, 3, 0x1234, 0xACE1, 0xFFFF)]
tex("t3b.tex", ["ziarno", "okres", "kolizje", "pierwsze 3 liczby"],
    [[r["ziarno"], sp(r["okres"]), r["kolizje"], ",\\,".join(map(str, r["pierwsze"][:3]))] for r in T3b], "rrrl")


T4 = [dict(b=b, **wiersz(1000, 1, b, 16, TAPY[16], 0xACE1)) for b in (1000, 10 ** 4, 65536, 10 ** 5, 10 ** 6)]
tex("t4.tex", ["zakres $[1,b]$", "bity $w$", "$w \\ge n$", "kolizje", "losowe (oczekiwane)"],
    [[sp(r["b"]), (r["b"] - 1).bit_length(), "tak" if (r["b"] - 1).bit_length() >= 16 else "nie", r["kolizje"], f"{r['losowe']:.1f}"]
     for r in T4], "rrrrr")


T5 = []
for n in (8, 12, 16, 18, 20):
    z = 0xACE1 & (2 ** n - 1)
    p1, p2 = okres(n, TAPY[n], z), okres_slownik(n, TAPY[n], z)
    T5.append(dict(n=n, p1=p1, p2=p2, t1=czas_ms(lambda: okres(n, TAPY[n], z)), t2=czas_ms(lambda: okres_slownik(n, TAPY[n], z))))
tex("t5.tex", ["$n$", "okres (kroki)", "okres (słownik)", "zgodne", "czas kroki [ms]", "czas słownik [ms]"],
    [[r["n"], sp(r["p1"]), sp(r["p2"]), "tak" if r["p1"] == r["p2"] else "NIE", f"{r['t1']:.1f}", f"{r['t2']:.1f}"] for r in T5], "rrrrrr")


T6 = [dict(K=K, ms=czas_ms(lambda: generuj(K, 1, 10 ** 6, 16, TAPY[16], 0xACE1))) for K in (10 ** 3, 10 ** 4, 10 ** 5)]
tex("t6.tex", ["$K$", "czas [ms]", "czas na liczbę [$\\mu$s]"],
    [[sp(r["K"]), f"{r['ms']:.1f}", f"{1000*r['ms']/r['K']:.1f}"] for r in T6], "rrr")

wyn.update(T1=T1, T2=T2, T3a=T3a, T3b=T3b, T4=T4, T5=T5, T6=T6)
json.dump(wyn, open("wyniki.json", "w"), indent=1, ensure_ascii=False)
print("gotowe: wyniki.json, t1..t6.tex, ciagi")
