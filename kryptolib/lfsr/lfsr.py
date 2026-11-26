from math import gcd


TAPY = {3: [3, 2], 4: [4, 3], 5: [5, 3], 6: [6, 5], 7: [7, 6], 8: [8, 6, 5, 4], 9: [9, 5],
        10: [10, 7], 11: [11, 9], 12: [12, 11, 10, 4], 13: [13, 12, 11, 8], 14: [14, 13, 12, 2],
        15: [15, 14], 16: [16, 15, 13, 4], 17: [17, 14], 18: [18, 11], 19: [19, 18, 17, 14],
        20: [20, 17], 21: [21, 19], 22: [22, 21], 23: [23, 18], 24: [24, 23, 22, 17]}


def sprawdz(n, tapy, ziarno):
    """Kontrola parametrów rejestru; przy błędzie zgłasza ValueError."""
    if not isinstance(n, int) or not 2 <= n <= 64:
        raise ValueError("długość rejestru n musi być liczbą całkowitą z [2, 64]")
    if not tapy or n not in tapy or any(not isinstance(t, int) or not 1 <= t <= n for t in tapy):
        raise ValueError("tapy: liczby z [1, n] i musi być wśród nich n (bit wyjściowy)")
    if not isinstance(ziarno, int) or not 1 <= ziarno < 2 ** n:
        raise ValueError("ziarno musi być z [1, 2^n - 1] (zero blokuje rejestr)")


def krok(stan, n, tapy):
    """Jeden takt rejestru: nowy bit = XOR bitów z pozycji 'tapy' (n = bit wyjściowy, 1 = najstarszy);
    stan przesuwa się w prawo, a nowy bit wchodzi z lewej."""
    bit = 0
    for t in tapy:
        bit ^= (stan >> (n - t)) & 1
    return (stan >> 1) | (bit << (n - 1))


def generuj(K, a, b, n, tapy, ziarno):
    """K liczb całkowitych z [a, b]: każda to w = bity(b-a) kolejnych bitów wyjściowych rejestru;
    wartość spoza zakresu jest odrzucana (bez modulo, więc rozkład nie jest przekrzywiony)."""
    sprawdz(n, tapy, ziarno)
    if K < 1 or a > b:
        raise ValueError("wymagane: K >= 1 oraz a <= b")
    w, stan, wynik = max(1, (b - a).bit_length()), ziarno, []
    for _ in range(1000 * K + 1000):
        x = 0
        for _ in range(w):
            x = (x << 1) | (stan & 1)
            stan = krok(stan, n, tapy)
        if x <= b - a:
            wynik.append(a + x)
            if len(wynik) == K:
                return wynik
    raise ValueError("nie udało się wygenerować K liczb dla tych parametrów")


def zapisz(plik, ciag):
    """Zapis ciągu do pliku tekstowego: jedna liczba w wierszu."""
    with open(plik, "w") as f:
        f.write("\n".join(map(str, ciag)) + "\n")


def wczytaj(plik):
    """Odczyt ciągu z pliku; czytelny błąd przy braku pliku lub złym formacie danych."""
    try:
        with open(plik) as f:
            return [int(x) for x in f.read().split()]
    except FileNotFoundError:
        raise ValueError(f"brak pliku: {plik}")
    except ValueError:
        raise ValueError(f"zły format danych w pliku {plik} (oczekiwane: liczby całkowite)")


def kolizje(ciag):
    """Liczba kolizji = ile liczb powtarza wcześniejszą wartość (K minus liczba różnych wartości)."""
    return len(ciag) - len(set(ciag))


def okres(n, tapy, ziarno):
    """Okres rejestru (metoda 1): liczba taktów, po których stan wraca do ziarna."""
    sprawdz(n, tapy, ziarno)
    stan = ziarno
    for k in range(1, 2 ** n + 1):
        stan = krok(stan, n, tapy)
        if stan == ziarno:
            return k


def cykl_liczb(n, tapy, ziarno, w):
    """Długość cyklu ciągu liczb składanych po w bitów: okres / NWD(okres, w)."""
    p = okres(n, tapy, ziarno)
    return p // gcd(p, w)


def bez_kolizji(K, a, b, ziarno=1):
    """Ciąg K liczb z [a, b] bez kolizji: rejestr o n = bity(b-a) i tapach maksymalnych daje w jednym okresie
    same różne wartości (bez zera, więc 'a' nie wystąpi). Zwraca (ciąg, parametry)."""
    n = max(3, (b - a).bit_length())
    if n not in TAPY or K > b - a:
        raise ValueError("brak tapów dla tego zakresu albo K większe niż liczba dostępnych wartości")
    ciag = generuj(K, a, b, n, TAPY[n], ziarno)
    if kolizje(ciag):
        raise ValueError("wystąpiły kolizje")
    return ciag, {"n": n, "tapy": TAPY[n], "ziarno": ziarno, "a": a, "b": b, "K": K}


if __name__ == "__main__":
    ciag = generuj(20, 1, 100, 16, TAPY[16], 0xACE1)
    print(ciag, "kolizje:", kolizje(ciag), "okres:", okres(16, TAPY[16], 0xACE1))
