"""Czytelne implementacje LFSR i LCG oraz wspólne narzędzia analizy."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from math import gcd
from typing import Iterable, Sequence


@dataclass(frozen=True)
class CycleInfo:
    """Długość części przedcyklicznej i właściwego cyklu stanu."""

    preperiod: int
    period: int
    states_examined: int


@dataclass(frozen=True)
class CollisionStats:
    """Statystyki powtórzeń wartości wynikowych, a nie stanów generatora."""

    count: int
    unique_count: int
    duplicate_occurrences: int
    repeated_values: int
    colliding_pairs: int


def collision_stats(values: Iterable[int]) -> CollisionStats:
    """Policz trzy jawnie nazwane miary kolizji w ciągu wartości."""

    materialized = list(values)
    counts = Counter(materialized)
    return CollisionStats(
        count=len(materialized),
        unique_count=len(counts),
        duplicate_occurrences=len(materialized) - len(counts),
        repeated_values=sum(1 for count in counts.values() if count > 1),
        colliding_pairs=sum(count * (count - 1) // 2 for count in counts.values()),
    )


def _validate_interval(lower: int, upper: int) -> int:
    if not isinstance(lower, int) or not isinstance(upper, int):
        raise TypeError("Granice przedziału muszą być liczbami całkowitymi.")
    if lower > upper:
        raise ValueError("Dolna granica przedziału nie może być większa od górnej.")
    return upper - lower + 1


class LFSR:
    """LFSR zgodny z rekurencją z notatki laboratoryjnej.

    Stan ``(S_i, ..., S_{i+n-1})`` zapisujemy od najstarszego bitu po lewej.
    Odczepy są indeksami 0-based w tym stanie. ``step`` zwraca ``S_i``, oblicza
    XOR bitów wskazanych przez odczepy, przesuwa stan w lewo i dopisuje bit
    sprzężenia po prawej.
    """

    def __init__(self, length: int, taps: Sequence[int], seed: Sequence[int]):
        if not isinstance(length, int) or length <= 0:
            raise ValueError("Długość rejestru musi być dodatnią liczbą całkowitą.")
        if len(seed) != length:
            raise ValueError("Ziarno musi mieć dokładnie tyle bitów co rejestr.")
        if any(bit not in (0, 1) for bit in seed):
            raise ValueError("Ziarno LFSR może zawierać tylko bity 0 i 1.")
        if not taps:
            raise ValueError("Lista odczepów nie może być pusta.")
        if any(not isinstance(tap, int) or tap < 0 or tap >= length for tap in taps):
            raise ValueError("Każdy odczep musi być indeksem z zakresu 0..n-1.")
        if len(set(taps)) != len(taps):
            raise ValueError("Odczepy nie mogą się powtarzać.")

        self.length = length
        self.taps = tuple(taps)
        self.state = tuple(seed)

    def step(self) -> int:
        output = self.state[0]
        feedback = 0
        for tap in self.taps:
            feedback ^= self.state[tap]
        self.state = self.state[1:] + (feedback,)
        return output

    def next_bits_as_int(self, bit_count: int) -> int:
        """Złóż kolejne bity wyjściowe w liczbę, od najstarszego do najmłodszego."""

        if not isinstance(bit_count, int) or bit_count <= 0:
            raise ValueError("Liczba bitów musi być dodatnia.")
        value = 0
        for _ in range(bit_count):
            value = (value << 1) | self.step()
        return value

    def draw_int(self, lower: int, upper: int) -> int:
        """Losuj bez obciążenia modulo, stosując rejection sampling."""

        size = _validate_interval(lower, upper)
        bit_count = max(1, (size - 1).bit_length())
        source_size = 1 << bit_count
        acceptance_limit = source_size - source_size % size
        states_at_candidate_start: set[tuple[int, ...]] = set()
        while True:
            if self.state in states_at_candidate_start:
                raise RuntimeError(
                    "Cykl LFSR nie zawiera kandydata akceptowanego przez mapowanie."
                )
            states_at_candidate_start.add(self.state)
            candidate = self.next_bits_as_int(bit_count)
            if candidate < acceptance_limit:
                return lower + candidate % size

    def generate(self, count: int, lower: int, upper: int) -> list[int]:
        if not isinstance(count, int) or count < 0:
            raise ValueError("K musi być nieujemną liczbą całkowitą.")
        _validate_interval(lower, upper)
        return [self.draw_int(lower, upper) for _ in range(count)]


def lfsr_cycle_info(
    length: int,
    taps: Sequence[int],
    seed: Sequence[int],
    max_steps: int | None = None,
) -> CycleInfo:
    """Wykryj pierwszy powtarzający się pełny stan metodą słownika."""

    generator = LFSR(length, taps, seed)
    seen: dict[tuple[int, ...], int] = {}
    step_index = 0
    while generator.state not in seen:
        if max_steps is not None and step_index >= max_steps:
            raise RuntimeError("Nie znaleziono cyklu przed osiągnięciem max_steps.")
        seen[generator.state] = step_index
        generator.step()
        step_index += 1
    first = seen[generator.state]
    return CycleInfo(first, step_index - first, len(seen))


class LCG:
    """Generator ``x_(i+1) = (a*x_i + c) mod m``.

    Notatka oznacza przyrost literą ``b``. W kodzie używamy zwyczajowego ``c``,
    aby nie pomylić go z górną granicą przedziału ``[a, b]``.
    """

    def __init__(self, modulus: int, multiplier: int, increment: int, seed: int):
        if not isinstance(modulus, int) or modulus <= 1:
            raise ValueError("Moduł m musi być liczbą całkowitą większą od 1.")
        if not all(isinstance(value, int) for value in (multiplier, increment, seed)):
            raise TypeError("Parametry a, c i x0 muszą być liczbami całkowitymi.")
        if not 0 <= multiplier < modulus:
            raise ValueError("Mnożnik a musi należeć do zakresu 0..m-1.")
        if not 0 <= increment < modulus:
            raise ValueError("Przyrost c musi należeć do zakresu 0..m-1.")
        if not 0 <= seed < modulus:
            raise ValueError("Ziarno x0 musi należeć do zakresu 0..m-1.")

        self.modulus = modulus
        self.multiplier = multiplier
        self.increment = increment
        self.state = seed

    def step(self) -> int:
        self.state = (
            self.multiplier * self.state + self.increment
        ) % self.modulus
        return self.state

    def draw_int(self, lower: int, upper: int) -> int:
        """Mapuj stan bez obciążenia modulo, odrzucając końcówkę 0..m-1."""

        size = _validate_interval(lower, upper)
        if size > self.modulus:
            raise ValueError(
                "Dla bezstronnego mapowania LCG rozmiar przedziału nie może "
                "przekraczać modułu m."
            )
        acceptance_limit = self.modulus - self.modulus % size
        seen_states: set[int] = set()
        while True:
            candidate = self.step()
            if candidate in seen_states:
                raise RuntimeError(
                    "Cykl LCG nie zawiera stanu akceptowanego przez mapowanie."
                )
            seen_states.add(candidate)
            if candidate < acceptance_limit:
                return lower + candidate % size

    def generate(self, count: int, lower: int, upper: int) -> list[int]:
        if not isinstance(count, int) or count < 0:
            raise ValueError("K musi być nieujemną liczbą całkowitą.")
        _validate_interval(lower, upper)
        return [self.draw_int(lower, upper) for _ in range(count)]


def lcg_cycle_info(
    modulus: int,
    multiplier: int,
    increment: int,
    seed: int,
    max_steps: int | None = None,
) -> CycleInfo:
    """Wykryj cykl pełnego stanu LCG, bez mylenia go z mapowanym wynikiem."""

    generator = LCG(modulus, multiplier, increment, seed)
    seen: dict[int, int] = {}
    step_index = 0
    while generator.state not in seen:
        if max_steps is not None and step_index >= max_steps:
            raise RuntimeError("Nie znaleziono cyklu przed osiągnięciem max_steps.")
        seen[generator.state] = step_index
        generator.step()
        step_index += 1
    first = seen[generator.state]
    return CycleInfo(first, step_index - first, len(seen))


def _distinct_prime_factors(value: int) -> set[int]:
    factors: set[int] = set()
    candidate = 2
    remaining = value
    while candidate * candidate <= remaining:
        if remaining % candidate == 0:
            factors.add(candidate)
            while remaining % candidate == 0:
                remaining //= candidate
        candidate += 1 if candidate == 2 else 2
    if remaining > 1:
        factors.add(remaining)
    return factors


def hull_dobell_conditions(modulus: int, multiplier: int, increment: int) -> dict[str, bool]:
    """Sprawdź warunki pełnego okresu mieszanego LCG (tw. Hulla-Dobella)."""

    if modulus <= 1:
        raise ValueError("Moduł musi być większy od 1.")
    prime_factors = _distinct_prime_factors(modulus)
    return {
        "gcd_c_m": gcd(increment, modulus) == 1,
        "prime_factors_divide_a_minus_1": all(
            (multiplier - 1) % factor == 0 for factor in prime_factors
        ),
        "four_condition": modulus % 4 != 0 or (multiplier - 1) % 4 == 0,
    }


def has_full_lcg_period(modulus: int, multiplier: int, increment: int) -> bool:
    return all(hull_dobell_conditions(modulus, multiplier, increment).values())
