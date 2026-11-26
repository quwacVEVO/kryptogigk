"""LCG - liniowy generator kongruencyjny (zakres grupy 2).

Konwencja (zgodna z notatką "Kryptologia lab05", slajd 2):

    x_0 = ziarno (seed)
    x_{i+1} = (a * x_i + c) mod m

UWAGA NA OZNACZENIA. W notatce przyrost oznaczony jest literą `b`
(`S_i = a*S_{i-1} + b mod m`). W tym projekcie przyrost nazywa się `c`,
ponieważ litery `a` i `b` są już zajęte przez końce przedziału `[a, b]`,
z którego losujemy liczby. Zatem:

    c (ten kod)  ==  b (notatka, przyrost)
    low, high (ten kod)  ==  a, b (treść zadania, przedział)

Mnożnik `a` z notatki to w tym kodzie pole `a` obiektu LCG - jego znaczenie
jest takie samo jak w notatce; kolizja nazw dotyczy wyłącznie przyrostu.

W notatce występuje też niespójność kolejności argumentów: na slajdzie 3 jest
`lcg(8121, 28411, 134456, 55)` przy sygnaturze `lcg(a,b,mod,seed)` (czyli
m = 134456), a na slajdzie 4 `LCG2(134456, 8121, 28411, 55)` przy sygnaturze
`LCG2(a,b,mod,seed)` (czyli m = 28411). Dlatego parametry przekazujemy tu
wyłącznie przez nazwy: LCG(m=..., a=..., c=..., x0=...).
"""

import argparse

from common import collision_report, find_cycle, write_numbers

MAX_DRAW_FACTOR = 1000


class LCG:
    """Generator liniowy kongruencyjny o konfigurowalnych m, a, c, x0."""

    def __init__(self, m, a, c, x0):
        for name, value in (("m", m), ("a", a), ("c", c), ("x0", x0)):
            if not isinstance(value, int) or isinstance(value, bool):
                raise ValueError("parametr {} musi być liczbą całkowitą, jest {!r}".format(name, value))
        if m < 2:
            raise ValueError("moduł m musi być >= 2, jest {}".format(m))
        if a < 0 or c < 0:
            raise ValueError("parametry a i c nie mogą być ujemne (a={}, c={})".format(a, c))
        if not 0 <= x0 < m:
            raise ValueError("ziarno x0 musi należeć do 0..m-1, jest {} przy m={}".format(x0, m))

        self.m = m
        self.a = a
        self.c = c
        self.x0 = x0
        self.state = x0

    # ---------------------------------------------------------- podstawowe operacje

    def reset(self):
        self.state = self.x0
        return self

    def next_state(self, state):
        """Czysta funkcja przejścia: (a*x + c) mod m."""
        return (self.a * state + self.c) % self.m

    def next_value(self):
        """Jeden krok: aktualizuje stan i zwraca NOWY stan x_{i+1}.

        Ziarno x_0 nie jest zwracane jako element ciągu wyjściowego (tak jak
        w pseudokodzie z notatki, gdzie pierwszy wynik to lcg(...) ziarna).
        """
        self.state = self.next_state(self.state)
        return self.state

    def states(self, count):
        """Lista `count` kolejnych stanów x_1, x_2, ..., x_count."""
        if count < 0:
            raise ValueError("liczba stanów nie może być ujemna")
        return [self.next_value() for _ in range(count)]

    # ---------------------------------------------------------- cykl

    def period(self, max_steps=200_000):
        """(ogon, cykl) dla ciągu STANÓW, licząc od x_0. Nie zmienia stanu obiektu.

        Ogon > 0 oznacza część przedcykliczną: stan x_0 nie wraca, generator
        "wpada" w cykl dopiero po kilku krokach (możliwe, gdy a nie jest
        odwracalne modulo m, np. gdy NWD(a, m) > 1).
        """
        return find_cycle(self.x0, self.next_state, max_steps=max_steps)

    # ---------------------------------------------------------- mapowanie na [low, high]

    def numbers(self, count, low, high, mode="mod_reject"):
        """`count` liczb całkowitych z przedziału [low, high].

        Stan generatora należy do 0..m-1; span = high - low + 1.

        mode="mod_reject" (domyślny) - odrzucamy stany x >= m - (m mod span),
            a pozostałe mapujemy jako low + x mod span. Jeśli stany są
            równomierne na 0..m-1, wynik jest równomierny na [low, high].
            Korzysta z NAJMNIEJ znaczących bitów stanu (dla m = 2^k są one
            najsłabsze - widać to w tabelach wpływu parametrów).
        mode="mod" - low + x mod span bez odrzucania (szybsze, ale obciążone,
            gdy span nie dzieli m).
        mode="scale" - low + (x * span) // m, czyli skalowanie liniowe;
            korzysta z NAJBARDZIEJ znaczących bitów stanu.
        """
        low, high, span = _validate_interval(low, high)
        if count < 0:
            raise ValueError("liczba liczb do wygenerowania nie może być ujemna")
        if mode not in ("mod_reject", "mod", "scale"):
            raise ValueError("nieznany tryb mapowania: {!r}".format(mode))

        usable = self.m - (self.m % span)
        if mode == "mod_reject" and usable == 0:
            raise ValueError(
                "przy m={} i przedziale o {} elementach tryb mod_reject odrzuca wszystkie "
                "stany (m < span); zwiększ m lub użyj trybu scale".format(self.m, span)
            )

        result = []
        attempts = 0
        limit = MAX_DRAW_FACTOR * max(count, 1) + MAX_DRAW_FACTOR
        while len(result) < count:
            attempts += 1
            if attempts > limit:
                raise RuntimeError(
                    "przekroczono limit {} prób losowania - sprawdź parametry generatora".format(limit)
                )
            state = self.next_value()
            if mode == "mod_reject":
                if state < usable:
                    result.append(low + state % span)
            elif mode == "mod":
                result.append(low + state % span)
            else:
                result.append(low + (state * span) // self.m)
        return result

    def unique_numbers(self, count, low, high, mode="mod_reject"):
        """`count` RÓŻNYCH liczb z [low, high] (filtr powtórzeń na ciągu wyjściowym)."""
        low, high, span = _validate_interval(low, high)
        if count > span:
            raise ValueError(
                "nie da się wygenerować {} różnych liczb z przedziału [{}, {}] "
                "o {} elementach (warunek K <= b - a + 1)".format(count, low, high, span)
            )
        seen = set()
        result = []
        attempts = 0
        limit = MAX_DRAW_FACTOR * max(count, 1) + MAX_DRAW_FACTOR
        while len(result) < count:
            attempts += 1
            if attempts > limit:
                raise RuntimeError(
                    "przekroczono limit {} prób - generator nie pokrywa całego przedziału "
                    "(prawdopodobnie zbyt krótki okres)".format(limit)
                )
            value = self.numbers(1, low, high, mode=mode)[0]
            if value not in seen:
                seen.add(value)
                result.append(value)
        return result

    # ---------------------------------------------------------- opis

    def describe(self):
        return "LCG m={} a={} c={} x0={}".format(self.m, self.a, self.c, self.x0)

    def __repr__(self):
        return "LCG(m={}, a={}, c={}, x0={})".format(self.m, self.a, self.c, self.x0)


# ---------------------------------------------------------------- warunki teoretyczne

def prime_factors(number):
    """Zbiór dzielników pierwszych liczby (prosty rozkład przez dzielenie próbne)."""
    if number < 2:
        return set()
    factors = set()
    remaining = number
    divisor = 2
    while divisor * divisor <= remaining:
        while remaining % divisor == 0:
            factors.add(divisor)
            remaining //= divisor
        divisor += 1 if divisor == 2 else 2
    if remaining > 1:
        factors.add(remaining)
    return factors


def gcd(first, second):
    """NWD algorytmem Euklidesa (własna implementacja, bez math.gcd)."""
    while second:
        first, second = second, first % second
    return first


def hull_dobell(m, a, c):
    """Warunki Hull-Dobella pełnego okresu m dla LCG z c > 0.

    Zwraca (czy_spełnione, lista_opisów_warunków). Spełnienie wszystkich trzech
    warunków oznacza okres równy m dla KAŻDEGO ziarna. Niespełnienie nie znaczy
    automatycznie, że okres jest krótki - trzeba go zmierzyć.
    """
    checks = []
    coprime = gcd(c, m) == 1
    checks.append(("NWD(c, m) = 1", coprime, "NWD({}, {}) = {}".format(c, m, gcd(c, m))))

    factors = prime_factors(m)
    divisible = all((a - 1) % p == 0 for p in factors)
    checks.append((
        "a - 1 podzielne przez każdy dzielnik pierwszy m",
        divisible,
        "dzielniki pierwsze m: {}, a-1 = {}".format(sorted(factors), a - 1),
    ))

    if m % 4 == 0:
        four = (a - 1) % 4 == 0
        checks.append(("m podzielne przez 4 => a - 1 podzielne przez 4", four,
                       "(a-1) mod 4 = {}".format((a - 1) % 4)))
    else:
        checks.append(("m niepodzielne przez 4 (warunek nie dotyczy)", True, "m mod 4 = {}".format(m % 4)))

    ok = c > 0 and all(result for _, result, _ in checks)
    if c == 0:
        checks.append(("c > 0 (warunki Hull-Dobella dotyczą c > 0)", False,
                       "c = 0 - generator multiplikatywny, inne kryterium okresu"))
    return ok, checks


def _validate_interval(low, high):
    if not isinstance(low, int) or isinstance(low, bool):
        raise ValueError("lewy koniec przedziału musi być liczbą całkowitą")
    if not isinstance(high, int) or isinstance(high, bool):
        raise ValueError("prawy koniec przedziału musi być liczbą całkowitą")
    if high < low:
        raise ValueError("pusty przedział: [{}, {}]".format(low, high))
    return low, high, high - low + 1


# ---------------------------------------------------------------- CLI

def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Generator LCG: generuje K liczb z [a,b] i zapisuje do pliku tekstowego."
    )
    parser.add_argument("--m", type=int, required=True, help="moduł m")
    parser.add_argument("--a", type=int, required=True, help="mnożnik a")
    parser.add_argument("--c", type=int, required=True, help="przyrost c (w notatce: b)")
    parser.add_argument("--x0", type=int, required=True, help="ziarno x0")
    parser.add_argument("--count", type=int, required=True, help="K - ile liczb wygenerować")
    parser.add_argument("--low", type=int, required=True, help="a - lewy koniec przedziału")
    parser.add_argument("--high", type=int, required=True, help="b - prawy koniec przedziału")
    parser.add_argument("--mode", choices=("mod_reject", "mod", "scale"), default="mod_reject",
                        help="tryb mapowania stanu na przedział (domyślnie mod_reject)")
    parser.add_argument("--unique", action="store_true", help="wymuś K różnych liczb")
    parser.add_argument("--out", help="plik wynikowy (bez tej opcji liczby idą na stdout)")
    args = parser.parse_args(argv)

    generator = LCG(m=args.m, a=args.a, c=args.c, x0=args.x0)
    if args.unique:
        numbers = generator.unique_numbers(args.count, args.low, args.high, mode=args.mode)
    else:
        numbers = generator.numbers(args.count, args.low, args.high, mode=args.mode)

    header = [
        generator.describe(),
        "K={} przedział=[{}, {}] mapowanie={}{}".format(
            args.count, args.low, args.high, args.mode, " +filtr różnych" if args.unique else ""
        ),
    ]
    if args.out:
        write_numbers(args.out, numbers, header)
        report = collision_report(numbers)
        print("zapisano {} liczb do {}".format(len(numbers), args.out))
        print("różnych wartości: {}, kolizji: {}".format(report["unique"], report["collisions"]))
    else:
        for line in header:
            print("# " + line)
        for value in numbers:
            print(value)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
