"""Moduł generatora LCG (Linear Congruential Generator) — Lab 05, Grupa 2 / Grupa 5.

Równanie rekurencyjne (zgodne z zadaniem Grupy 2):
    x_{i+1} = (a * x_i + c) mod m,   x_0 = ziarno (seed)

Uwaga terminologiczna względem notatki wykładowej (T. Gzella, slajd 2/14):
    W notatce przyrost oznaczono literą `b`:  S_i = (a * S_{i-1} + b) mod m.
    W niniejszej implementacji przyrost oznaczamy jako `c`, aby uniknąć kolizji
    oznaczeń z przedziałem docelowym [a_min, b_max] (w zadaniu [a, b]).
    W funkcjach przedział docelowy nazywamy `low` i `high` (odpowiednio `a` i `b` z zadania).
"""

from __future__ import annotations

import math
from pathlib import Path
from typing import Iterable, Iterator, Sequence


class LCGParameterError(ValueError):
    """Wyjątek zgłaszany przy niepoprawnych parametrach generatora LCG."""


class LCGDataFormatError(ValueError):
    """Wyjątek zgłaszany przy błędnym formacie danych wejściowych/plikowych."""


def validate_lcg_params(m: int, a: int, c: int, x0: int) -> tuple[int, int, int, int]:
    """Waliduje parametry LCG: m >= 2, 0 <= a < m (lub dowolne a >= 1), 0 <= c < m, 0 <= x0 < m."""
    for name, val in (("m", m), ("a", a), ("c", c), ("x0", x0)):
        if isinstance(val, bool) or not isinstance(val, int):
            raise LCGParameterError(f"Parametr {name} musi być liczbą całkowitą.")
    if m < 2:
        raise LCGParameterError(f"Moduł m musi spełniać warunek m >= 2 (podano {m}).")
    if a <= 0:
        raise LCGParameterError(f"Mnożnik a musi być dodatnią liczbą całkowitą (podano {a}).")
    if c < 0:
        raise LCGParameterError(f"Przyrost c musi być nieujemną liczbą całkowitą (podano {c}).")
    if x0 < 0:
        raise LCGParameterError(f"Ziarno x0 musi być nieujemną liczbą całkowitą (podano {x0}).")
    return m, a, c, x0 % m


def _distinct_prime_factors(n: int) -> list[int]:
    """Zwraca posortowaną listę unikalnych dzielników pierwszych liczby n >= 2."""
    factors: list[int] = []
    temp = n
    d = 2
    while d * d <= temp:
        if temp % d == 0:
            factors.append(d)
            while temp % d == 0:
                temp //= d
        d += 1 if d == 2 else 2
    if temp > 1:
        factors.append(temp)
    return factors


def check_hull_dobell(m: int, a: int, c: int) -> dict[str, object]:
    """Sprawdza warunki twierdzenia Hulla–Dobella dla okresu maksymalnego (= m) LCG (dla c > 0).

    Twierdzenie Hulla–Dobella:
        Generator LCG z c != 0 ma okres równy dokładnie m wtedy i tylko wtedy, gdy:
        1. NWD(m, c) = 1,
        2. (a - 1) jest podzielne przez każdy dzielnik pierwszy liczby m,
        3. jeśli 4 dzieli m, to 4 dzieli również (a - 1).
    """
    validate_lcg_params(m, a, c, 0)
    cond1_coprime = (c > 0) and (math.gcd(m, c) == 1)
    prime_factors = _distinct_prime_factors(m)
    cond2_primes = all((a - 1) % p == 0 for p in prime_factors)
    cond3_div4 = True if (m % 4 != 0) else ((a - 1) % 4 == 0)
    full_period = cond1_coprime and cond2_primes and cond3_div4
    return {
        "m": m,
        "a": a,
        "c": c,
        "prime_factors_of_m": prime_factors,
        "cond1_gcd_m_c_eq_1": cond1_coprime,
        "cond2_a_minus_1_div_all_primes": cond2_primes,
        "cond3_div4_rule": cond3_div4,
        "has_maximal_period_m": full_period,
    }


class LCG:
    """Generator liniowy kongruencyjny x_{i+1} = (a * x_i + c) mod m."""

    def __init__(self, m: int, a: int, c: int, x0: int) -> None:
        self.m, self.a, self.c, self.x0 = validate_lcg_params(m, a, c, x0)
        self._state = self.x0

    @property
    def state(self) -> int:
        """Zwraca bieżący stan x_i."""
        return self._state

    def reset(self) -> None:
        """Resetuje generator do ziarna x0."""
        self._state = self.x0

    def next_state(self) -> int:
        """Wyznacza i zwraca kolejny stan x_{i+1} = (a * x_i + c) mod m."""
        self._state = (self.a * self._state + self.c) % self.m
        return self._state

    def stream(self) -> Iterator[int]:
        """Nieskończony iterator kolejnych stanów x_1, x_2, ... (odpowiednik LCG2 z yield)."""
        while True:
            yield self.next_state()

    def generate_integers(
        self,
        k: int,
        low: int,
        high: int,
        mapping: str = "scale",
    ) -> list[int]:
        """Generuje K liczb całkowitych z przedziału domkniętego [low, high].

        Obsługiwane mapowania ze stanu x w {0, ..., m - 1} do [low, high] (span = high - low + 1):
            - mapping="scale" (zalecane): low + (x * span) // m.
              Wykorzystuje najbardziej znaczące bity stanu x, co eliminuje typową wadę
              LCG z m = 2^k, w których najmłodsze bity mają bardzo krótkie cykle.
            - mapping="mod": low + (x % span).
              Proste mapowanie resztą z dzielenia; dla m = 2^k i parzystego `span`
              powoduje naprzemienność parzystości lub skrócenie okresu dolnych bitów.
        """
        validate_range_and_count(k, low, high)
        if mapping not in ("scale", "mod"):
            raise LCGParameterError("Dozwolone tryby mapowania to 'scale' lub 'mod'.")

        span = high - low + 1
        result: list[int] = []
        for _ in range(k):
            x = self.next_state()
            if mapping == "scale":
                mapped = low + (x * span) // self.m
            else:
                mapped = low + (x % span)
            result.append(mapped)
        return result


def validate_range_and_count(k: int, low: int, high: int) -> None:
    """Waliduje liczbę elementów K oraz przedział [low, high]."""
    for name, val in (("K", k), ("a (low)", low), ("b (high)", high)):
        if isinstance(val, bool) or not isinstance(val, int):
            raise LCGParameterError(f"Parametr {name} musi być liczbą całkowitą.")
    if k < 1:
        raise LCGParameterError("Liczba generowanych wartości K musi być >= 1.")
    if low > high:
        raise LCGParameterError(f"Niepoprawny przedział: a ({low}) > b ({high}).")


def analyze_collisions(numbers: Sequence[int]) -> dict[str, object]:
    """Analizuje powtórzenia i kolizje w ciągu wynikowych liczb."""
    seen: dict[int, int] = {}
    counts: dict[int, int] = {}
    first_collision_index: int | None = None
    first_collision_value: int | None = None

    for idx, val in enumerate(numbers):
        counts[val] = counts.get(val, 0) + 1
        if val in seen and first_collision_index is None:
            first_collision_index = idx
            first_collision_value = val
        elif val not in seen:
            seen[val] = idx

    unique_count = len(counts)
    total_collisions = len(numbers) - unique_count
    repeated_values = {v: c for v, c in counts.items() if c > 1}
    max_multiplicity = max(counts.values()) if counts else 0

    return {
        "count": len(numbers),
        "unique_count": unique_count,
        "total_collisions": total_collisions,
        "collision_rate": (total_collisions / len(numbers)) if numbers else 0.0,
        "repeated_unique_values": len(repeated_values),
        "max_multiplicity": max_multiplicity,
        "first_collision_index": first_collision_index,
        "first_collision_value": first_collision_value,
    }


def detect_state_cycle(
    m: int,
    a: int,
    c: int,
    x0: int,
    max_steps: int = 500_000,
) -> dict[str, object]:
    """Wyznacza część przedcykliczną (mu) i długość cyklu stanu (lambda) metodą Floyda.

    Algorytm żółwia i zająca (Floyd) wymaga O(1) pamięci i wykrywa zarówno część
    przedcykliczną `preperiod` (mu), jak i długość cyklu `cycle_length` (lambda),
    startując od stanu początkowego x_0.
    Jeżeli cykl przekracza `max_steps`, zwraca `measured=False` wraz z weryfikacją
    analityczną z twierdzenia Hulla–Dobella.
    """
    m, a, c, x0 = validate_lcg_params(m, a, c, x0)
    hd = check_hull_dobell(m, a, c)

    def f(x: int) -> int:
        return (a * x + c) % m

    tortoise = f(x0)
    hare = f(f(x0))
    steps = 1
    while tortoise != hare:
        if steps >= max_steps:
            return {
                "measured": False,
                "preperiod": 0 if hd["has_maximal_period_m"] else None,
                "cycle_length": m if hd["has_maximal_period_m"] else None,
                "cycle_source": "hull_dobell_theorem" if hd["has_maximal_period_m"] else "exceeded_limit",
                "hull_dobell": hd,
            }
        tortoise = f(tortoise)
        hare = f(f(hare))
        steps += 1

    # Wyznaczenie początku cyklu (mu)
    preperiod = 0
    tortoise = x0
    while tortoise != hare:
        tortoise = f(tortoise)
        hare = f(hare)
        preperiod += 1

    # Wyznaczenie długości cyklu (lambda)
    cycle_length = 1
    hare = f(tortoise)
    while tortoise != hare:
        hare = f(hare)
        cycle_length += 1

    return {
        "measured": True,
        "preperiod": preperiod,
        "cycle_length": cycle_length,
        "cycle_source": "floyd_measured",
        "hull_dobell": hd,
    }


def generate_collision_free_sequence(
    k: int,
    low: int,
    high: int,
    m: int,
    a: int,
    c: int,
    x0: int,
    mapping: str = "scale",
) -> list[int]:
    """Generuje K liczb z [low, high] i sprawdza brak kolizji (wraz z warunkiem K <= high - low + 1)."""
    validate_range_and_count(k, low, high)
    span = high - low + 1
    if k > span:
        raise LCGParameterError(
            f"Niemożliwe wygenerowanie K={k} unikalnych liczb z przedziału [{low}, {high}] "
            f"(rozmiar przedziału to {span}, wymagane K <= b - a + 1)."
        )
    gen = LCG(m=m, a=a, c=c, x0=x0)
    seq = gen.generate_integers(k=k, low=low, high=high, mapping=mapping)
    stats = analyze_collisions(seq)
    if stats["total_collisions"] != 0:
        raise LCGParameterError(
            f"Dla podanych parametrów wystąpiło {stats['total_collisions']} kolizji "
            f"(pierwsza na indeksie {stats['first_collision_index']})."
        )
    return seq


def save_numbers_to_file(
    filepath: str | Path,
    numbers: Iterable[int],
    header_comments: Sequence[str] | None = None,
) -> Path:
    """Zapisuje wygenerowane liczby do pliku tekstowego (po jednej w linii)."""
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []
    if header_comments:
        for comment in header_comments:
            lines.append(f"# {comment}")
    for n in numbers:
        if isinstance(n, bool) or not isinstance(n, int):
            raise LCGDataFormatError(f"Próba zapisu wartości niecałkowitej: {n!r}")
        lines.append(str(n))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def load_numbers_from_file(filepath: str | Path) -> list[int]:
    """Wczytuje liczby całkowite z pliku tekstowego z obsługą błędów pliku i formatu."""
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Plik z liczbami nie istnieje: {path}")
    if not path.is_file():
        raise LCGDataFormatError(f"Ścieżka nie jest plikiem: {path}")

    numbers: list[int] = []
    for line_no, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            continue
        try:
            numbers.append(int(stripped))
        except ValueError as exc:
            raise LCGDataFormatError(
                f"Błędny format danych w pliku {path}, linia {line_no}: {raw!r}"
            ) from exc

    if not numbers:
        raise LCGDataFormatError(f"Plik {path} nie zawiera żadnych liczb całkowitych.")
    return numbers
