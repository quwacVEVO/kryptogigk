import math
import time


def rozloz_na_potegi_pierwsze(n: int) -> list[int]:
    """Rozkłada liczbę n na parami względnie pierwsze potęgi liczb pierwszych."""

    # n = 28 -> (4, 7)
    moduly: list[int] = []
    dzielnik = 2
    while dzielnik * dzielnik <= n:
        if n % dzielnik == 0:
            potega = 1
            while n % dzielnik == 0:
                potega *= dzielnik
                n //= dzielnik
            moduly.append(potega)
        dzielnik += 1
    if n > 1:
        moduly.append(n)
    return moduly


def logarytm_dyskretny(g_podgrupy: int, h_podgrupy: int, p: int, rzad: int) -> int:
    """Rozwiązuje mniejsze równanie (g_podgrupy)^a = h_podgrupy (mod p) w podgrupie o znanym rzędzie metodą Baby-step Giant-step."""

    # krok = sufit z pierwiastka z |G|, a = i*krok + j
    krok = math.isqrt(rzad) + 1 

    # Krok mały (Baby-step): zapisujemy kolejne potęgi g^j (mod p) dla j = 0, ..., krok-1
    male_kroki: dict[int, int] = {}
    aktualna_wartosc = 1
    for j in range(krok):
        male_kroki[aktualna_wartosc] = j
        aktualna_wartosc = (aktualna_wartosc * g_podgrupy) % p

    # Krok wielki (Giant-step): obliczamy g^(-krok) (mod p)
    skok_wstecz = pow(g_podgrupy, -krok, p)
    gamma = h_podgrupy

    for i in range(krok):
        if gamma in male_kroki:
            return i * krok + male_kroki[gamma]
        gamma = (gamma * skok_wstecz) % p

    raise ValueError("Nie znaleziono rozwiązania logarytmu dyskretnego.")


def chinskie_twierdzenie_o_resztach(reszty: list[int], moduly: list[int]) -> int:
    """Łączy wyniki za pomocą Chińskiego Twierdzenia o Resztach metodą podstawiania."""

    a = reszty[0]
    aktualny_modul = moduly[0]

    for i in range(1, len(moduly)):
        nastepna_reszta = reszty[i]
        nastepny_modul = moduly[i]

        roznica = (nastepna_reszta - a) % nastepny_modul
        odwrotnosc = pow(aktualny_modul, -1, nastepny_modul)
        k = (roznica * odwrotnosc) % nastepny_modul

        a = a + aktualny_modul * k
        aktualny_modul *= nastepny_modul

    return a


def pohlig_hellman(p: int, g: int, h: int) -> int:
    """Algorytm Pohliga-Hellmana."""

    rzad_grupy = p - 1
    moduly = rozloz_na_potegi_pierwsze(rzad_grupy)

    print(f"Rząd grupy |G| = p - 1 = {p} - 1 = {rzad_grupy} = {' * '.join(map(str, moduly))}\n")

    reszty: list[int] = []

    print("Rozwiązujemy mniejsze problemy logarytmu dyskretnego:")

    for modul in moduly:
        wykladnik = rzad_grupy // modul
        g_podgrupy = pow(g, wykladnik, p)
        h_podgrupy = pow(h, wykladnik, p)

        reszta_a = logarytm_dyskretny(g_podgrupy, h_podgrupy, p, modul)
        reszty.append(reszta_a)

        # (g^((p-1)/modul[i]))^a = h^(p-1)/modul[i]) : (g')^a = (h') (mod p) => a = x (mod modul[i])
        print(f"  (g^{wykladnik})^a = h^{wykladnik}:  {g_podgrupy}^a = {h_podgrupy} (mod {p})  =>  a = {reszta_a} (mod {modul})")

    print("\nŁączymy wyniki za pomocą chińskiego twierdzenia o resztach.")

    return chinskie_twierdzenie_o_resztach(reszty, moduly)

if __name__ == "__main__":
    print("--- Z1. ---")

    p = 37781
    g = 3
    h = 24581

    print(f"Dane: p = {p}, g = {g}, h = {h}")

    start = time.perf_counter()
    a = pohlig_hellman(p, g, h)
    czas = time.perf_counter() - start

    print(f"\nOtrzymujemy: a = {a}")
    print(f"Sprawdzenie: {g}^{a} mod {p} = {pow(g, a, p)} (oczekiwano {h})\n")

    print(f"Czas wykonania: {czas:.6f} sekundy ({czas * 1000:.3f} ms)")

