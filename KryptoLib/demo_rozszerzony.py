"""KryptoLib - rozszerzona demonstracja podpunktu 3 (szyfr monoalfabetyczny).

Przechodzi przez WSZYSTKIE funkcje modułu `monoalfabetyczny` na wymagających
przykładach: polski tekst z diakrytykami, cyfry, spacje, losowe klucze, klucze
z hasła, skrajne przesunięcia, błędne dane, długi tekst, zapis do pliku oraz
łamanie szyfru Cezara metodą brute force.

Wykorzystuje całą bibliotekę: preprocessing (część 1), szyfr afiniczny (część 2)
oraz szyfr monoalfabetyczny (część 3).
"""

import os
import random
import re
import time

from kryptolib import afiniczny as af
from kryptolib import klucze as kl
from kryptolib import monoalfabetyczny as m
from kryptolib import preprocessing as prep

# ---------------------------------------------------------------------------
# Pomocnicze
# ---------------------------------------------------------------------------
LICZNIK = {"ok": 0, "blad": 0}


def sprawdz(opis, warunek):
    LICZNIK["ok" if warunek else "blad"] += 1
    print(f"   [{'OK' if warunek else 'BŁĄD'}] {opis}")


def naglowek(tekst):
    print("\n" + "=" * 78)
    print(tekst)
    print("=" * 78)


def losowy_klucz(mode, seed):
    znaki = list(m.get_alphabet(mode))
    random.Random(seed).shuffle(znaki)
    return "".join(znaki)


def klucz_z_hasla(haslo, mode):
    """Klucz permutacyjny z hasła: unikalne znaki hasła, potem reszta alfabetu."""
    alfabet = m.get_alphabet(mode)
    wynik = []
    for c in haslo.upper() + alfabet:
        if c in alfabet and c not in wynik:
            wynik.append(c)
    return "".join(wynik)


def probuj(funkcja, *args, **kw):
    """Zwraca tekst błędu ValueError albo None, gdy błędu nie było."""
    try:
        funkcja(*args, **kw)
    except ValueError as e:
        return str(e)
    return None


# ---------------------------------------------------------------------------
# Dane wejściowe
# ---------------------------------------------------------------------------
SUROWY = (
    "Zażółć gęślą jaźń! W 2026 roku, 4 października, o godz. 22:30 "
    "w Gdańsku padało 17 mm deszczu. Kod dostępu: PG-4711 (Łódź → Źródło)."
)

# ===========================================================================
naglowek("0. DANE WEJŚCIOWE I PREPROCESSING")
print(f"Tekst surowy:\n   {SUROWY}")
T26 = prep.tryb_alfa26(SUROWY)
T37 = prep.tryb_alfa37(SUROWY)
print(f"ALFA26: {T26}")
print(f"ALFA37: {T37}")
TEKSTY = {"ALFA26": T26, "ALFA37": T37}
sprawdz("tekst ALFA26 zawiera tylko A-Z", set(T26) <= set(m.ALFA26))
sprawdz("tekst ALFA37 zawiera tylko A-Z, 0-9 i spację", set(T37) <= set(m.ALFA37))

# ===========================================================================
naglowek("1. ALFABETY: get_alphabet, ALFA26, ALFA37")
sprawdz("ALFA26 ma 26 znaków", len(m.ALFA26) == 26)
sprawdz("ALFA37 ma 37 znaków (A-Z, 0-9, spacja)", len(m.ALFA37) == 37 and m.ALFA37[-1] == " ")
sprawdz("get_alphabet nie zależy od wielkości liter nazwy trybu", m.get_alphabet("alfa37") == m.ALFA37)
print("   Nieznany tryb ->", probuj(m.get_alphabet, "ALFA99"))
sprawdz("nieznany tryb zgłasza ValueError", probuj(m.get_alphabet, "ALFA99") is not None)

# ===========================================================================
naglowek("2. SZYFR OGÓLNY: encrypt / decrypt, losowe klucze i klucze z hasła")
for mode in ("ALFA26", "ALFA37"):
    tekst = TEKSTY[mode]
    print(f"\n -- tryb {mode} --")
    klucz = losowy_klucz(mode, seed=2026)
    c = m.encrypt(tekst, klucz, mode)
    print(f"   klucz losowy: {klucz!r}")
    print(f"   jawny:        {tekst}")
    print(f"   kryptogram:   {c}")
    sprawdz("deszyfrowanie odtwarza tekst jawny", m.decrypt(c, klucz, mode) == tekst)
    sprawdz("kryptogram ma tę samą długość co tekst", len(c) == len(tekst))
    sprawdz("monoalfabetyczność: ten sam znak jawny -> zawsze ten sam znak szyfrowy",
            all(len({c[i] for i in range(len(tekst)) if tekst[i] == ch}) == 1 for ch in set(tekst)))

    klucz2 = klucz_z_hasla("KRYPTOGRAFIA", mode)
    c2 = m.encrypt(tekst, klucz2, mode)
    print(f"   klucz z hasła KRYPTOGRAFIA: {klucz2!r}")
    print(f"   kryptogram:   {c2}")
    sprawdz("klucz z hasła jest poprawną permutacją", probuj(m.validate_key, klucz2, mode) is None)
    sprawdz("deszyfrowanie kluczem z hasła działa", m.decrypt(c2, klucz2, mode) == tekst)

    sprawdz("zły klucz nie odszyfruje poprawnie", m.decrypt(c, klucz2, mode) != tekst)
    sprawdz("pusty tekst -> pusty kryptogram", m.encrypt("", klucz, mode) == "")

# ===========================================================================
naglowek("3. KLUCZ ODWROTNY: invert_key")
for mode in ("ALFA26", "ALFA37"):
    k = losowy_klucz(mode, 7)
    ki = m.invert_key(k, mode)
    print(f" {mode}: klucz    {k!r}\n         odwrotny {ki!r}")
    sprawdz("odwrotność odwrotności to klucz pierwotny", m.invert_key(ki, mode) == k)
    sprawdz("szyfrowanie kluczem odwrotnym == deszyfrowanie kluczem pierwotnym",
            m.encrypt(TEKSTY[mode], ki, mode) == m.decrypt(TEKSTY[mode], k, mode))

# ===========================================================================
naglowek("4. WALIDACJA KLUCZA: validate_key (komunikaty o błędach)")
zle = [
    ("za krótki (3 znaki)", "ABC", "ALFA26"),
    ("za długi (27 znaków)", m.ALFA26 + "A", "ALFA26"),
    ("powtórzone znaki", "A" * 26, "ALFA26"),
    ("cyfra w kluczu ALFA26", m.ALFA26[:-1] + "1", "ALFA26"),
    ("małe litery", m.ALFA26.lower(), "ALFA26"),
    ("klucz 26 znaków w trybie ALFA37", m.ALFA26, "ALFA37"),
    ("klucz 37 znaków w trybie ALFA26", m.ALFA37, "ALFA26"),
    ("ALFA37 bez spacji (spacja zastąpiona '!')", m.ALFA37[:-1] + "!", "ALFA37"),
]
for opis, k, mode in zle:
    msg = probuj(m.validate_key, k, mode)
    print(f"   {opis}\n       -> {msg}")
    sprawdz(f"odrzucono: {opis}", msg is not None)
sprawdz("poprawny klucz identycznościowy akceptowany", probuj(m.validate_key, m.ALFA37, "ALFA37") is None)

# ===========================================================================
naglowek("5. ZNAKI SPOZA ALFABETU")
for opis, tekst, mode in [
    ("małe litery", "ala ma kota", "ALFA26"),
    ("spacja w ALFA26", "ALA MA KOTA", "ALFA26"),
    ("cyfra w ALFA26", "AGENT007", "ALFA26"),
    ("diakrytyk", "ŻÓŁĆ", "ALFA37"),
    ("interpunkcja", "TAK!", "ALFA37"),
]:
    msg = probuj(m.encrypt, tekst, m.caesar_key(1, mode), mode)
    print(f"   {opis}: {tekst!r} -> {msg}")
    sprawdz(f"odrzucono: {opis}", msg is not None)

# ===========================================================================
naglowek("6. CEZAR: caesar_key, caesar_encrypt, caesar_decrypt")
t = T26
print(f"   jawny: {t}")
for s in (1, 3, 13, 25, 26, 27, -1, -3, 1000, -1000):
    print(f"   przesunięcie {s:>6}: klucz {m.caesar_key(s, 'ALFA26')}  ->  {m.caesar_encrypt(t, s)[:30]}...")
sprawdz("przesunięcie 0 i 26 dają ten sam klucz (ALFA26)", m.caesar_key(0) == m.caesar_key(26) == m.ALFA26)
sprawdz("przesunięcie 0 i 37 to identyczność (ALFA37)", m.caesar_key(37, "ALFA37") == m.caesar_key(0, "ALFA37") == m.ALFA37)
sprawdz("przesunięcie ujemne = dodatnie modulo 26", m.caesar_key(-3) == m.caesar_key(23))
sprawdz("klasyczne: A->D, X->A przy przesunięciu 3", m.caesar_encrypt("AX", 3) == "DA")
sprawdz("klasyczne: 'VENI VIDI VICI' z przesunięciem 3 w ALFA37",
        m.caesar_encrypt("VENI VIDI VICI", 3, "ALFA37") == "YHQLCYLGLCYLFL")
for mode in ("ALFA26", "ALFA37"):
    n = len(m.get_alphabet(mode))
    sprawdz(f"{mode}: round-trip dla wszystkich przesunięć od {-2 * n} do {2 * n}",
            all(m.caesar_decrypt(m.caesar_encrypt(TEKSTY[mode], s, mode), s, mode) == TEKSTY[mode]
                for s in range(-2 * n, 2 * n + 1)))
a, b = 5, 11
sprawdz("złożenie Cezara +5 i +11 = Cezar +16",
        m.caesar_encrypt(m.caesar_encrypt(t, a), b) == m.caesar_encrypt(t, a + b))
sprawdz("w ALFA37 cyfry też się przesuwają (Z->0 przy +1)", m.caesar_encrypt("Z", 1, "ALFA37") == "0")
sprawdz("w ALFA37 spacja przechodzi w A przy +1", m.caesar_encrypt(" ", 1, "ALFA37") == "A")

# ===========================================================================
naglowek("7. ATBASZ: atbash_key, atbash_encrypt, atbash_decrypt")
print(f"   klucz ALFA26: {m.atbash_key()}")
print(f"   klucz ALFA37: {m.atbash_key('ALFA37')!r}")
sprawdz("A<->Z, B<->Y", m.atbash_encrypt("ABYZ") == "ZYBA")
for mode in ("ALFA26", "ALFA37"):
    c = m.atbash_encrypt(TEKSTY[mode], mode)
    print(f"   {mode}: {c}")
    sprawdz(f"{mode}: atbash jest inwolucją (dwukrotne szyfrowanie = jawny)", m.atbash_encrypt(c, mode) == TEKSTY[mode])
    sprawdz(f"{mode}: atbash_decrypt odwraca atbash_encrypt", m.atbash_decrypt(c, mode) == TEKSTY[mode])
    sprawdz(f"{mode}: atbash_key == invert_key(atbash_key)", m.atbash_key(mode) == m.invert_key(m.atbash_key(mode), mode))
sprawdz("w ALFA37: A<->spacja", m.atbash_encrypt("A", "ALFA37") == " ")

# ===========================================================================
naglowek("8. ROT13: rot13_key, rot13_encrypt, rot13_decrypt")
print(f"   klucz ALFA26: {m.rot13_key()}")
print(f"   klucz ALFA37: {m.rot13_key('ALFA37')!r}")
sprawdz("klasyk: HELLO -> URYYB", m.rot13_encrypt("HELLO") == "URYYB")
sprawdz("ALFA26: ROT13 == Cezar z przesunięciem 13", m.rot13_key() == m.caesar_key(13))
for mode in ("ALFA26", "ALFA37"):
    c = m.rot13_encrypt(TEKSTY[mode], mode)
    print(f"   {mode}: {c}")
    sprawdz(f"{mode}: ROT13 dwukrotnie = tekst jawny", m.rot13_encrypt(c, mode) == TEKSTY[mode])
    sprawdz(f"{mode}: rot13_decrypt == rot13_encrypt", m.rot13_decrypt(c, mode) == m.rot13_encrypt(c, mode))
sprawdz("ALFA37: cyfry i spacja bez zmian, litery przesunięte", m.rot13_encrypt("AB 19 Z", "ALFA37") == "NO 19 M")
sprawdz("ALFA37: ROT13 różni się od Cezara +13 (cyfry!)", m.rot13_key("ALFA37") != m.caesar_key(13, "ALFA37"))

# ===========================================================================
naglowek("9. GADERYPOLUKI: gaderypoluki_key, _encrypt, _decrypt, własne frazy")
for nazwa, fraza in m.GADERYPOLUKI_FRAZY.items():
    k = m.gaderypoluki_key(fraza)
    print(f"   {nazwa}: pary {' '.join(fraza[i:i+2] for i in range(0, len(fraza), 2))}")
    print(f"      klucz: {k}")
    for mode in ("ALFA26", "ALFA37"):
        c = m.gaderypoluki_encrypt(TEKSTY[mode], fraza, mode)
        sprawdz(f"{nazwa}/{mode}: round-trip i inwolucja",
                m.gaderypoluki_decrypt(c, fraza, mode) == TEKSTY[mode] and
                m.gaderypoluki_encrypt(c, fraza, mode) == TEKSTY[mode])
sprawdz("klasyka: 'ALAMAKOTA' -> 'GUGMGIPTG' (GA-DE-RY-PO-LU-KI)", m.gaderypoluki_encrypt("ALAMAKOTA") == "GUGMGIPTG")
sprawdz("dla frazy domyślnej P<->O, L<->U", m.gaderypoluki_encrypt("PL") == "OU")
sprawdz("fraza pisana małymi literami jest akceptowana", m.gaderypoluki_key("gaderypoluki") == m.gaderypoluki_key("GADERYPOLUKI"))
own = "MALINOWEGY"
print(f"   własna fraza {own}: {m.gaderypoluki_encrypt('MALINA', own)}")
sprawdz("własna 5-parowa fraza działa jako inwolucja", m.gaderypoluki_encrypt(m.gaderypoluki_encrypt('MALINOWY', own), own) == "MALINOWY")
for opis, fraza in [("nieparzysta liczba liter", "ABC"), ("powtórzone litery", "ABAC"), ("znaki spoza A-Z", "A1")]:
    msg = probuj(m.gaderypoluki_key, fraza)
    print(f"   zła fraza ({opis}): {msg}")
    sprawdz(f"odrzucono frazę: {opis}", msg is not None)

# ===========================================================================
naglowek("10. SZYFRY SZCZEGÓLNE vs SZYFR OGÓLNY (funkcje pomocnicze = encrypt z kluczem)")
for mode in ("ALFA26", "ALFA37"):
    t = TEKSTY[mode]
    sprawdz(f"{mode}: caesar_encrypt == encrypt(caesar_key)", m.caesar_encrypt(t, 7, mode) == m.encrypt(t, m.caesar_key(7, mode), mode))
    sprawdz(f"{mode}: atbash_encrypt == encrypt(atbash_key)", m.atbash_encrypt(t, mode) == m.encrypt(t, m.atbash_key(mode), mode))
    sprawdz(f"{mode}: rot13_encrypt == encrypt(rot13_key)", m.rot13_encrypt(t, mode) == m.encrypt(t, m.rot13_key(mode), mode))
    sprawdz(f"{mode}: gaderypoluki_encrypt == encrypt(gaderypoluki_key)",
            m.gaderypoluki_encrypt(t, "POLITYKARENU", mode) == m.encrypt(t, m.gaderypoluki_key("POLITYKARENU", mode), mode))

# ===========================================================================
naglowek("11. TEST OBCIĄŻENIOWY: 200 000 znaków, 200 losowych kluczy na krótkich tekstach")
rng = random.Random(1)
dlugi = "".join(rng.choice(m.ALFA37) for _ in range(200_000))
k = losowy_klucz("ALFA37", 99)
start = time.perf_counter()
c = m.encrypt(dlugi, k, "ALFA37")
d = m.decrypt(c, k, "ALFA37")
czas = time.perf_counter() - start
print(f"   szyfrowanie + deszyfrowanie 200 000 znaków: {czas:.3f} s")
sprawdz("długi tekst: round-trip", d == dlugi)
ok = 0
for i in range(200):
    mode = rng.choice(("ALFA26", "ALFA37"))
    tekst = "".join(rng.choice(m.get_alphabet(mode)) for _ in range(rng.randint(0, 80)))
    kk = losowy_klucz(mode, i)
    ok += m.decrypt(m.encrypt(tekst, kk, mode), kk, mode) == tekst
sprawdz("200/200 losowych round-tripów (różne tryby, długości 0-80)", ok == 200)

# ===========================================================================
naglowek("12. ŁAMANIE CEZARA METODĄ BRUTE FORCE (ALFA26)")
tajny = m.caesar_encrypt(prep.tryb_alfa26("Szyfr Cezara jest bardzo prosty do złamania, wystarczy sprawdzić wszystkie przesunięcia"), 17)
print(f"   przechwycony kryptogram: {tajny}")
# Prosta ocena "polskości": udział najczęstszych polskich liter
CZESTE = "AIEOZNRWSYC"
ocena = []
for s in range(26):
    kandydat = m.caesar_decrypt(tajny, s)
    wynik = sum(kandydat.count(ch) for ch in CZESTE) / len(kandydat)
    ocena.append((wynik, s, kandydat))
for wynik, s, kandydat in sorted(ocena, reverse=True)[:3]:
    print(f"   przesunięcie {s:>2}, ocena {wynik:.2f}: {kandydat[:50]}...")
najlepsze = max(ocena)
sprawdz("brute force + analiza częstości wskazało przesunięcie 17", najlepsze[1] == 17)

# ===========================================================================
naglowek("13. POTOK PEŁNY: plik -> preprocessing -> szyfr -> kolumny -> plik -> deszyfrowanie")
folder = os.path.dirname(os.path.abspath(__file__))
plik_in = os.path.join(folder, "demo_jawny.txt")
plik_out = os.path.join(folder, "demo_zaszyfrowany.txt")
prep.zapisz_do_pliku(plik_in, SUROWY)
wczytany = prep.wczytaj_z_pliku(plik_in)
czysty = prep.tryb_alfa26(wczytany)
klucz = klucz_z_hasla("POLITECHNIKA", "ALFA26")
kryptogram = m.encrypt(czysty, klucz)
w_kolumnach = prep.podziel_na_kolumny(kryptogram, kolumny=4, grupy=5)
prep.zapisz_do_pliku(plik_out, w_kolumnach)
print(f"   klucz (hasło POLITECHNIKA): {klucz}")
print(f"   kryptogram w kolumnach zapisany do {os.path.basename(plik_out)}:\n")
print("\n".join("      " + w for w in w_kolumnach.splitlines()))
odczyt = prep.wczytaj_z_pliku(plik_out)
bez_spacji = re.sub(r"\s+", "", odczyt)
sprawdz("po wczytaniu z pliku i usunięciu białych znaków kryptogram jest ten sam", bez_spacji == kryptogram)
sprawdz("deszyfrowanie z pliku odtwarza tekst po preprocessingu", m.decrypt(bez_spacji, klucz) == czysty)
print(f"   odszyfrowano: {m.decrypt(bez_spacji, klucz)}")

# ===========================================================================
naglowek("14. SZYFR AFINICZNY (część 2) i jego spójność z szyfrem ogólnym")
for mode in ("ALFA26", "ALFA37"):
    t = TEKSTY[mode]
    n = len(m.get_alphabet(mode))
    dozwolone = af.poprawne_a(mode)
    print(f"\n -- tryb {mode}: m = {n}, dopuszczalne a: {dozwolone if n == 26 else '1..36 (37 jest liczbą pierwszą)'}")
    a, b = (5, 8) if mode == "ALFA26" else (7, 12)
    c = af.szyfruj_afiniczny(t, a, b, mode)
    print(f"   a={a}, b={b}, a^-1={af.odwrotnosc_modularna(a, n)}")
    print(f"   jawny:      {t}")
    print(f"   kryptogram: {c}")
    sprawdz("deszyfrowanie afiniczne odtwarza tekst jawny", af.deszyfruj_afiniczny(c, a, b, mode) == t)
    kl_aff = kl.affine_key(a, b, mode)
    print(f"   klucz permutacyjny tego szyfru: {kl_aff!r}")
    sprawdz("szyfr afiniczny == szyfr ogólny z kluczem afinicznym", m.encrypt(t, kl_aff, mode) == c)
    sprawdz("Cezar o s to afiniczny a=1, b=s", m.caesar_encrypt(t, 9, mode) == af.szyfruj_afiniczny(t, 1, 9, mode))
    sprawdz("Atbash to afiniczny a=m-1, b=m-1", m.atbash_encrypt(t, mode) == af.szyfruj_afiniczny(t, n - 1, n - 1, mode))
    klucze_aff = {kl.affine_key(x, y, mode) for x in dozwolone for y in range(n)}
    print(f"   różnych kluczy afinicznych: {len(klucze_aff)} (= {len(dozwolone)} x {n})")
    sprawdz("każda para (a, b) daje inny klucz", len(klucze_aff) == len(dozwolone) * n)
for opis, a_zle, mode in [("a=2 (nie jest względnie pierwsze z 26)", 2, "ALFA26"),
                          ("a=13", 13, "ALFA26"), ("a=0", 0, "ALFA26"),
                          ("a=37 w ALFA37", 37, "ALFA37")]:
    msg = probuj(af.szyfruj_afiniczny, "A", a_zle, 1, mode)
    print(f"   zły klucz {opis}: {msg}")
    sprawdz(f"odrzucono: {opis}", msg is not None)
msg = probuj(af.szyfruj_afiniczny, "Ala ma kota", 5, 8)
print(f"   surowy tekst do szyfru afinicznego: {msg}")
sprawdz("szyfr afiniczny nie czyści tekstu po cichu (jak szyfr ogólny)", msg is not None)

# ===========================================================================
naglowek("PODSUMOWANIE")
print(f"   Sprawdzeń zakończonych sukcesem: {LICZNIK['ok']}")
print(f"   Sprawdzeń zakończonych błędem:   {LICZNIK['blad']}")
print("   WYNIK:", "WSZYSTKO DZIAŁA" if LICZNIK["blad"] == 0 else "SĄ BŁĘDY - patrz [BŁĄD] powyżej")

if __name__ == "__main__":
    input("\nNaciśnij Enter, aby zamknąć okno...")
