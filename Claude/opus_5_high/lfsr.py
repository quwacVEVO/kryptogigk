"""LFSR - rejestr przesuwny z liniowym sprzężeniem zwrotnym (zakres grupy 1).

Konwencja (zgodna z notatką "Kryptologia lab05", slajd 6):

    S = seed = (S_0, ..., S_{n-1}) in Z_2^n
    S_{i+n} = suma_{j=0}^{n-1} p_j * S_{i+j}  (mod 2)

Przyjęte jednoznaczne ustalenia (identyczne dla wszystkich eksperymentów):

* STAN       - lista n bitów `state`, gdzie state[0] to S_i (bit najstarszy
               pod względem kolejności wyjścia), a state[n-1] to S_{i+n-1}.
* BIT WYJŚCIOWY - state[0], czyli bit opuszczający rejestr w danym kroku.
* KIERUNEK PRZESUWANIA - w lewo: (S_0, ..., S_{n-1}) -> (S_1, ..., S_{n-1}, S_n),
               nowy bit sprzężenia dopisywany jest na końcu (z prawej).
* ODCZEPY    - wektor p = (p_0, ..., p_{n-1}); p_j mnoży state[j], więc indeks
               odczepu j liczony jest OD BITU WYJŚCIOWEGO. `from_tap_indices`
               przyjmuje zbiór indeksów j, dla których p_j = 1.
* WIELOMIAN  - podstawiając S_i = x^i otrzymujemy x^n = suma p_j x^j, czyli
               wielomian charakterystyczny f(x) = x^n + suma_{j} p_j x^j (mod 2).
               Okresu maksymalnego (2^n - 1) nie deklarujemy z góry - jest mierzony
               metodą `period()`.
* p_0 = 0    - dopuszczalne, ale wtedy odwzorowanie stanu nie jest bijekcją,
               więc może pojawić się część przedcykliczna (ogon > 0). Pokazane
               w tabeli wpływu odczepów (exp_lfsr.py).
"""

import argparse

from common import collision_report, find_cycle, write_numbers

MAX_DRAW_FACTOR = 1000  # zabezpieczenie przed nieskończonym losowaniem przy odrzucaniu


def bits_from_int(value, n):
    """Zamienia liczbę na n bitów; bit najbardziej znaczący trafia na state[0]."""
    if value < 0:
        raise ValueError("ziarno jako liczba nie może być ujemne")
    if value >= (1 << n):
        raise ValueError("ziarno {} nie mieści się w {} bitach".format(value, n))
    return [(value >> (n - 1 - i)) & 1 for i in range(n)]


def int_from_bits(bits):
    """Zamienia listę bitów na liczbę; bits[0] jest bitem najbardziej znaczącym."""
    value = 0
    for bit in bits:
        value = (value << 1) | bit
    return value


def bits_needed(span):
    """Liczba bitów potrzebna do zapisania wartości z zakresu 0..span-1."""
    if span < 1:
        raise ValueError("zakres musi mieć co najmniej jedną wartość")
    return (span - 1).bit_length()


def _validate_bit_vector(vector, n, name):
    values = list(vector)
    if len(values) != n:
        raise ValueError("{} ma długość {}, oczekiwano {}".format(name, len(values), n))
    for value in values:
        if value not in (0, 1):
            raise ValueError("{} zawiera wartość {!r}, dopuszczalne są tylko 0 i 1".format(name, value))
    return values


class LFSR:
    """Generator LFSR o konfigurowalnej długości, odczepach i ziarnie."""

    def __init__(self, n, taps, seed, allow_zero_seed=False):
        if not isinstance(n, int) or isinstance(n, bool):
            raise ValueError("długość rejestru n musi być liczbą całkowitą")
        if n < 2:
            raise ValueError("długość rejestru n musi być >= 2, jest {}".format(n))

        self.n = n
        self.taps = _validate_bit_vector(taps, n, "wektor odczepów p")
        if sum(self.taps) == 0:
            raise ValueError("wszystkie odczepy są zerowe - brak sprzężenia zwrotnego")

        seed_bits = _validate_bit_vector(seed, n, "ziarno S")
        if sum(seed_bits) == 0 and not allow_zero_seed:
            raise ValueError(
                "ziarno zerowe daje ciąg stale równy 0; użyj allow_zero_seed=True, "
                "jeśli chcesz zbadać ten przypadek brzegowy"
            )
        self.seed = list(seed_bits)
        self.state = list(seed_bits)

    # ---------------------------------------------------------- konstruktory

    @classmethod
    def from_tap_indices(cls, n, tap_indices, seed, allow_zero_seed=False):
        """Buduje LFSR z listy indeksów odczepów j (tych, dla których p_j = 1)."""
        taps = [0] * n
        for index in tap_indices:
            if not isinstance(index, int) or isinstance(index, bool):
                raise ValueError("indeks odczepu musi być liczbą całkowitą, jest {!r}".format(index))
            if not 0 <= index < n:
                raise ValueError("indeks odczepu {} poza zakresem 0..{}".format(index, n - 1))
            taps[index] = 1
        if isinstance(seed, int) and not isinstance(seed, bool):
            seed = bits_from_int(seed, n)
        return cls(n, taps, seed, allow_zero_seed=allow_zero_seed)

    # ---------------------------------------------------------- podstawowe operacje

    def reset(self):
        """Przywraca stan początkowy (ziarno)."""
        self.state = list(self.seed)
        return self

    def state_bits(self):
        return tuple(self.state)

    def state_int(self):
        return int_from_bits(self.state)

    def feedback_bit(self):
        """Nowy bit sprzężenia: suma p_j * S_j mod 2 dla bieżącego stanu."""
        total = 0
        for tap, bit in zip(self.taps, self.state):
            total ^= tap & bit
        return total

    def next_bit(self):
        """Jeden krok generatora: zwraca bit wyjściowy i przesuwa rejestr w lewo."""
        out = self.state[0]
        new_bit = self.feedback_bit()
        self.state = self.state[1:] + [new_bit]
        return out

    def bits(self, count):
        """Lista `count` kolejnych bitów wyjściowych."""
        if count < 0:
            raise ValueError("liczba bitów nie może być ujemna")
        return [self.next_bit() for _ in range(count)]

    def words(self, count, width):
        """Lista `count` liczb złożonych z `width` kolejnych bitów (pierwszy bit = najstarszy).

        Słowa są rozłączne (nie zachodzą na siebie): zużywamy width bitów na słowo.
        """
        if width < 0:
            raise ValueError("szerokość słowa nie może być ujemna")
        return [int_from_bits(self.bits(width)) if width else 0 for _ in range(count)]

    # ---------------------------------------------------------- cykl

    def step_state_int(self, state_int):
        """Czysta funkcja przejścia na reprezentacji całkowitej (do wykrywania cyklu)."""
        bits = bits_from_int(state_int, self.n)
        new_bit = 0
        for tap, bit in zip(self.taps, bits):
            new_bit ^= tap & bit
        return int_from_bits(bits[1:] + [new_bit])

    def period(self, max_steps=200_000):
        """(ogon, cykl) dla ciągu STANÓW, licząc od ziarna. Nie zmienia stanu obiektu."""
        return find_cycle(int_from_bits(self.seed), self.step_state_int, max_steps=max_steps)

    def ones_ratio(self, count):
        """Udział jedynek w `count` bitach wyjściowych (prosty test monobitowy)."""
        sample = self.bits(count)
        return sum(sample) / len(sample) if sample else 0.0

    # ---------------------------------------------------------- mapowanie na [low, high]

    def numbers(self, count, low, high, mode="reject"):
        """`count` liczb całkowitych z przedziału [low, high].

        Mapowanie (jawne, identyczne w całym projekcie):
          span = high - low + 1, width = ceil(log2(span)) bitów na jedną próbę,
          bity składane są od najstarszego (pierwszy wygenerowany bit = najstarszy),
          v = wartość słowa z zakresu 0..2^width - 1.

        mode="reject" (domyślny) - jeśli v >= span, słowo jest odrzucane i losowane
            jest następne; rozkład na [low, high] jest wtedy równomierny, ale liczba
            zużytych bitów jest zmienna (średnio width * 2^width / span bitów na liczbę).
        mode="mod" - wartość low + v % span; żadne słowo nie jest odrzucane, ale gdy
            span nie jest potęgą dwójki, mniejsze wartości przedziału są
            uprzywilejowane (obciążenie modulo). Zostawione do porównania.
        """
        low, high, span = _validate_interval(low, high)
        if count < 0:
            raise ValueError("liczba liczb do wygenerowania nie może być ujemna")
        if mode not in ("reject", "mod"):
            raise ValueError("nieznany tryb mapowania: {!r}".format(mode))

        width = bits_needed(span)
        result = []
        attempts = 0
        limit = MAX_DRAW_FACTOR * max(count, 1) + MAX_DRAW_FACTOR
        while len(result) < count:
            attempts += 1
            if attempts > limit:
                raise RuntimeError(
                    "przekroczono limit {} prób losowania - sprawdź parametry generatora".format(limit)
                )
            value = int_from_bits(self.bits(width)) if width else 0
            if mode == "reject":
                if value < span:
                    result.append(low + value)
            else:
                result.append(low + value % span)
        return result

    def unique_numbers(self, count, low, high, mode="reject"):
        """`count` RÓŻNYCH liczb z [low, high]: wartości już użyte są pomijane.

        To filtr nałożony na ciąg wyjściowy (a nie zmiana generatora) - trzeba go
        wykazać w sprawozdaniu, bo zmienia rozkład odstępów między liczbami.
        Warunek wykonalności: count <= high - low + 1.
        """
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

    def tap_indices(self):
        return tuple(j for j, tap in enumerate(self.taps) if tap)

    def polynomial(self):
        """Wielomian charakterystyczny w postaci tekstowej."""
        parts = ["x^{}".format(self.n)]
        for j in sorted(self.tap_indices(), reverse=True):
            parts.append("x^{}".format(j) if j > 1 else ("x" if j == 1 else "1"))
        return " + ".join(parts)

    def describe(self):
        return (
            "LFSR n={} p={} (odczepy j={}) f(x)={} ziarno={} (0b{})".format(
                self.n,
                "".join(str(b) for b in self.taps),
                ",".join(str(j) for j in self.tap_indices()),
                self.polynomial(),
                int_from_bits(self.seed),
                "".join(str(b) for b in self.seed),
            )
        )

    def __repr__(self):
        return "LFSR(n={}, taps={}, seed={})".format(self.n, self.taps, self.seed)


def _validate_interval(low, high):
    """Sprawdza poprawność przedziału [low, high] i zwraca (low, high, liczba elementów)."""
    if not isinstance(low, int) or isinstance(low, bool):
        raise ValueError("lewy koniec przedziału musi być liczbą całkowitą")
    if not isinstance(high, int) or isinstance(high, bool):
        raise ValueError("prawy koniec przedziału musi być liczbą całkowitą")
    if high < low:
        raise ValueError("pusty przedział: [{}, {}]".format(low, high))
    return low, high, high - low + 1


def check_k_fits_interval(count, low, high):
    """Sprawdza warunek K <= b - a + 1 i zwraca (czy_ok, komunikat)."""
    _, _, span = _validate_interval(low, high)
    if count <= span:
        return True, "K={} <= b-a+1={} - ciąg bez powtórzeń jest możliwy".format(count, span)
    return False, (
        "K={} > b-a+1={} - ciąg K różnych liczb z [{}, {}] jest NIEMOŻLIWY "
        "(zasada szufladkowa)".format(count, span, low, high)
    )


# ---------------------------------------------------------------- CLI

def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Generator LFSR: generuje K liczb z [a,b] i zapisuje do pliku tekstowego."
    )
    parser.add_argument("--n", type=int, required=True, help="długość rejestru")
    parser.add_argument("--taps", required=True,
                        help="odczepy: albo ciąg bitów p (np. 1010100000000001), albo indeksy j "
                             "oddzielone przecinkami (np. 0,2,3,5)")
    parser.add_argument("--seed", required=True,
                        help="ziarno: ciąg bitów (np. 1010...) albo liczba całkowita")
    parser.add_argument("--count", type=int, required=True, help="K - ile liczb wygenerować")
    parser.add_argument("--low", type=int, required=True, help="a - lewy koniec przedziału")
    parser.add_argument("--high", type=int, required=True, help="b - prawy koniec przedziału")
    parser.add_argument("--mode", choices=("reject", "mod"), default="reject",
                        help="tryb mapowania bitów na przedział (domyślnie reject)")
    parser.add_argument("--unique", action="store_true",
                        help="wymuś K różnych liczb (filtr powtórzeń)")
    parser.add_argument("--out", help="plik wynikowy (bez tej opcji liczby idą na stdout)")
    args = parser.parse_args(argv)

    taps = _parse_taps(args.taps, args.n)
    seed = _parse_seed(args.seed, args.n)

    generator = LFSR(args.n, taps, seed)
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


def _parse_taps(text, n):
    """Przyjmuje albo ciąg n bitów ("1100...") albo listę indeksów ("0,2,3,5")."""
    cleaned = text.strip()
    is_bit_vector = len(cleaned) == n and set(cleaned) <= {"0", "1"}
    if is_bit_vector:
        return [int(ch) for ch in cleaned]
    indices = {int(part) for part in cleaned.split(",") if part.strip()}
    return [1 if j in indices else 0 for j in range(n)]


def _parse_seed(text, n):
    cleaned = text.strip()
    if len(cleaned) == n and set(cleaned) <= {"0", "1"}:
        return [int(ch) for ch in cleaned]
    return bits_from_int(int(cleaned), n)


if __name__ == "__main__":
    raise SystemExit(main())
