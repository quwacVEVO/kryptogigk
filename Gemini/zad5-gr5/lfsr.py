"""Moduł generatora LFSR (Linear Feedback Shift Register) — Lab 05, Grupa 1 / Grupa 5.

Konwencja matematyczna (zgodna z notatką wykładową T. Gzelli, slajd 6/14):
    Stan rejestru o długości n:
        S = (S_0, S_1, ..., S_{n-1}) w Z_2^n
    Współczynniki sprzężenia zwrotnego:
        p = (p_0, p_1, ..., p_{n-1}) w Z_2^n
    Indeksy odczepów (taps):
        taps = [j dla j w 0..n-1, gdzie p_j = 1]
    Równanie rekurencyjne (krok przesunięcia w lewo):
        bit_wyjsciowy = S_0
        bit_nowy = (sum_{j in taps} S_j) mod 2  (XOR bitów na pozycjach taps)
        nowy_stan = (S_1, S_2, ..., S_{n-1}, bit_nowy)

Dzięki temu kolejne bity wyjściowe tworzą dokładnie ciąg S_0, S_1, ..., S_{n-1}, S_n, S_{n+1}, ...
gdzie S_{i+n} = sum_{j=0}^{n-1} p_j * S_{i+j} mod 2.
"""

from __future__ import annotations

import math
from pathlib import Path
from typing import Iterable, Sequence


class LFSRParameterError(ValueError):
    """Wyjątek zgłaszany przy niepoprawnych parametrach generatora LFSR."""


class LFSRDataFormatError(ValueError):
    """Wyjątek zgłaszany przy błędnym formacie danych wejściowych/plikowych."""


def taps_from_coefficients(coefficients: Sequence[int]) -> tuple[int, ...]:
    """Konwertuje wektor współczynników p = (p_0, ..., p_{n-1}) na posortowaną krotkę odczepów."""
    if not isinstance(coefficients, Sequence) or isinstance(coefficients, (str, bytes)):
        raise LFSRParameterError("Wektor współczynników p musi być sekwencją bitów 0/1.")
    if len(coefficients) == 0:
        raise LFSRParameterError("Wektor współczynników p nie może być pusty.")
    taps: list[int] = []
    for idx, bit in enumerate(coefficients):
        if isinstance(bit, bool) or bit not in (0, 1):
            raise LFSRParameterError(
                f"Współczynnik p[{idx}] = {bit!r} nie jest poprawnym bitem (dozwolone: 0 lub 1)."
            )
        if bit == 1:
            taps.append(idx)
    return tuple(taps)


def validate_lfsr_params(
    length: int,
    taps: Sequence[int],
    seed: Sequence[int],
    allow_zero_seed: bool = False,
) -> tuple[int, tuple[int, ...], tuple[int, ...]]:
    """Waliduje parametry LFSR: długość rejestru, listę odczepów oraz ziarno."""
    if isinstance(length, bool) or not isinstance(length, int) or length < 2:
        raise LFSRParameterError("Długość rejestru n musi być liczbą całkowitą >= 2.")

    if not isinstance(taps, Sequence) or isinstance(taps, (str, bytes)):
        raise LFSRParameterError("Odczepy (taps) muszą być sekwencją indeksów całkowitych.")
    if len(taps) == 0:
        raise LFSRParameterError("Lista odczepów (taps) nie może być pusta.")

    normalized_taps: list[int] = []
    for t in taps:
        if isinstance(t, bool) or not isinstance(t, int):
            raise LFSRParameterError(f"Indeks odczepu {t!r} musi być liczbą całkowitą.")
        if t < 0 or t >= length:
            raise LFSRParameterError(
                f"Indeks odczepu {t} wykracza poza zakres [0, {length - 1}]."
            )
        normalized_taps.append(t)

    if len(set(normalized_taps)) != len(normalized_taps):
        raise LFSRParameterError("Indeksy odczepów nie mogą się powtarzać.")

    if not isinstance(seed, Sequence) or isinstance(seed, (str, bytes)):
        raise LFSRParameterError("Ziarno (seed) musi być sekwencją bitów 0/1.")
    if len(seed) != length:
        raise LFSRParameterError(
            f"Długość ziarna ({len(seed)}) musi być równa długości rejestru ({length})."
        )

    normalized_seed: list[int] = []
    for idx, bit in enumerate(seed):
        if isinstance(bit, bool) or bit not in (0, 1):
            raise LFSRParameterError(
                f"Bit ziarna seed[{idx}] = {bit!r} musi mieć wartość 0 lub 1."
            )
        normalized_seed.append(bit)

    if not allow_zero_seed and all(b == 0 for b in normalized_seed):
        raise LFSRParameterError(
            "Ziarno złożone wyłącznie z zer prowadzi do zdegenerowanego cyklu długości 1 (same zera)."
        )

    return length, tuple(sorted(normalized_taps)), tuple(normalized_seed)


class LFSR:
    """Rejestr przesuwny z liniowym sprzężeniem zwrotnym (Fibonacci LFSR, przesuwanie w lewo)."""

    def __init__(
        self,
        length: int,
        taps: Sequence[int],
        seed: Sequence[int],
        allow_zero_seed: bool = False,
    ) -> None:
        self.length, self.taps, self.initial_seed = validate_lfsr_params(
            length=length,
            taps=taps,
            seed=seed,
            allow_zero_seed=allow_zero_seed,
        )
        self._state: list[int] = list(self.initial_seed)

    @classmethod
    def from_coefficients(
        cls,
        coefficients: Sequence[int],
        seed: Sequence[int],
        allow_zero_seed: bool = False,
    ) -> "LFSR":
        """Tworzy LFSR bezpośrednio z wektora p = (p_0, ..., p_{n-1}) z notatki wykładowej."""
        taps = taps_from_coefficients(coefficients)
        return cls(
            length=len(coefficients),
            taps=taps,
            seed=seed,
            allow_zero_seed=allow_zero_seed,
        )

    @property
    def state(self) -> tuple[int, ...]:
        """Zwraca aktualny stan rejestru jako krotkę bitów."""
        return tuple(self._state)

    def reset(self) -> None:
        """Przywraca rejestr do ziarna początkowego."""
        self._state = list(self.initial_seed)

    def step(self) -> int:
        """Wykonuje jeden krok rejestru i zwraca bit wyjściowy S_i (najstarszy bit S[0])."""
        output_bit = self._state[0]
        feedback = 0
        for tap in self.taps:
            feedback ^= self._state[tap]
        self._state = self._state[1:] + [feedback]
        return output_bit

    def generate_bits(self, count: int) -> list[int]:
        """Generuje dokładną liczbę `count` kolejnych bitów."""
        if isinstance(count, bool) or not isinstance(count, int) or count < 0:
            raise LFSRParameterError("Liczba bitów `count` musi być nieujemną liczbą całkowitą.")
        return [self.step() for _ in range(count)]

    def next_word(self, bit_width: int) -> int:
        """Składa `bit_width` kolejnych bitów (MSB-first) w nieujemną liczbę całkowitą."""
        if isinstance(bit_width, bool) or not isinstance(bit_width, int) or bit_width < 1:
            raise LFSRParameterError("Szerokość słowa `bit_width` musi być liczbą całkowitą >= 1.")
        value = 0
        for _ in range(bit_width):
            value = (value << 1) | self.step()
        return value

    def generate_integers(
        self,
        k: int,
        a: int,
        b: int,
        bit_width: int | None = None,
        mapping: str = "mod",
        max_rejection_attempts: int = 1_000_000,
    ) -> list[int]:
        """Generuje K liczb całkowitych z przedziału domkniętego [a, b].

        Parametry mapowania:
            - mapping="mod": składa `w` bitów w liczbę v i wylicza `a + (v % span)`.
              Proste i deterministyczne czasowo, lecz dla span niebędącego potęgą 2
              wprowadza lekką nierównomierność (wartości mniejsze od `2^w mod span`
              mogą występować o 1 raz częściej w pełnym cyklu słów).
            - mapping="rejection": odrzuca słowa v >= span, dzięki czemu rozkład
              na przedziale [a, b] nie ma obciążenia modulo (wymaga jednak
              wystarczająco różnorodnego strumienia bitów).
        """
        validate_range_and_count(k, a, b)
        if mapping not in ("mod", "rejection"):
            raise LFSRParameterError("Dozwolone tryby mapowania to 'mod' lub 'rejection'.")

        span = b - a + 1
        if span == 1:
            return [a] * k

        min_bits = math.ceil(math.log2(span))
        width = min_bits if bit_width is None else bit_width
        if isinstance(width, bool) or not isinstance(width, int) or width < 1:
            raise LFSRParameterError("Szerokość bitowa `bit_width` musi być >= 1.")

        numbers: list[int] = []
        if mapping == "mod":
            for _ in range(k):
                word = self.next_word(width)
                numbers.append(a + (word % span))
            return numbers

        # Tryb rejection sampling
        if width < min_bits:
            raise LFSRParameterError(
                f"Dla mapping='rejection' wymagane jest bit_width >= {min_bits} (podano {width})."
            )
        attempts = 0
        while len(numbers) < k:
            attempts += 1
            if attempts > max_rejection_attempts:
                raise LFSRParameterError(
                    "Przekroczono limit prób w trybie rejection sampling — generator może "
                    "być uwięziony w krótkim cyklu poza przedziałem [a, b]."
                )
            word = self.next_word(width)
            if word < span:
                numbers.append(a + word)
        return numbers


def validate_range_and_count(k: int, a: int, b: int) -> None:
    """Waliduje K oraz przedział [a, b]."""
    for name, val in (("K", k), ("a", a), ("b", b)):
        if isinstance(val, bool) or not isinstance(val, int):
            raise LFSRParameterError(f"Parametr {name} musi być liczbą całkowitą.")
    if k < 1:
        raise LFSRParameterError("Liczba generowanych wartości K musi być >= 1.")
    if a > b:
        raise LFSRParameterError(f"Niepoprawny przedział: a ({a}) > b ({b}).")


def analyze_collisions(numbers: Sequence[int]) -> dict[str, object]:
    """Analizuje powtórzenia i kolizje w wygenerowanym ciągu liczb.

    Definicja kolizji:
        - `total_collisions = len(numbers) - len(set(numbers))`: łączna liczba
          nadmiarowych wystąpień (ile razy wygenerowana wartość pojawiła się już wcześniej).
        - `repeated_unique_values`: liczba unikalnych wartości, które wystąpiły >= 2 razy.
        - `first_collision_index`: indeks (0-based) pierwszego powtórzenia albo None.
    """
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
    length: int,
    taps: Sequence[int],
    seed: Sequence[int],
    max_steps: int = 500_000,
    allow_zero_seed: bool = False,
) -> dict[str, int | bool | None]:
    """Wyznacza długość części przedcyklicznej (mu) oraz cyklu stanu (lambda) dla LFSR.

    Metoda: zapis pierwszego kroku pojawienia się każdego stanu rejestru jako maski bitowej.
    Gdy aktualny stan pojawia się ponownie w kroku `step`, to:
        mu = seen[state]
        lambda = step - seen[state]
    """
    gen = LFSR(length=length, taps=taps, seed=seed, allow_zero_seed=allow_zero_seed)
    seen: dict[tuple[int, ...], int] = {}
    for step in range(max_steps + 1):
        st = gen.state
        if st in seen:
            preperiod = seen[st]
            period = step - preperiod
            max_theoretical = (1 << length) - 1
            return {
                "found": True,
                "preperiod": preperiod,
                "cycle_length": period,
                "max_theoretical_period": max_theoretical,
                "is_maximal": (period == max_theoretical and preperiod == 0),
            }
        seen[st] = step
        gen.step()

    return {
        "found": False,
        "preperiod": None,
        "cycle_length": None,
        "max_theoretical_period": (1 << length) - 1,
        "is_maximal": False,
    }


def detect_output_word_cycle(
    length: int,
    taps: Sequence[int],
    seed: Sequence[int],
    a: int,
    b: int,
    bit_width: int | None = None,
    mapping: str = "mod",
    max_words: int = 200_000,
) -> dict[str, int | bool | None]:
    """Wykrywa cykl na poziomie pary (stan_przed_słowem, wygenerowana_liczba) — czyli
    rzeczywisty okres ciągu wynikowych liczb po składaniu bitów i mapowaniu do [a, b].
    """
    validate_range_and_count(1, a, b)
    span = b - a + 1
    width = (1 if span == 1 else math.ceil(math.log2(span))) if bit_width is None else bit_width
    gen = LFSR(length=length, taps=taps, seed=seed)
    seen_states: dict[tuple[int, ...], int] = {}

    for idx in range(max_words + 1):
        st = gen.state
        if st in seen_states:
            preperiod = seen_states[st]
            return {
                "found": True,
                "preperiod_words": preperiod,
                "word_cycle_length": idx - preperiod,
            }
        seen_states[st] = idx
        if mapping == "mod":
            gen.next_word(width)
        else:
            while True:
                w = gen.next_word(width)
                if w < span:
                    break

    return {
        "found": False,
        "preperiod_words": None,
        "word_cycle_length": None,
    }


def generate_collision_free_sequence(
    k: int,
    a: int,
    b: int,
    length: int,
    taps: Sequence[int],
    seed: Sequence[int],
    bit_width: int | None = None,
    mapping: str = "mod",
) -> list[int]:
    """Generuje ciąg K liczb z [a, b] i weryfikuje, że nie zawiera żadnych kolizji.

    Sprawdza warunek konieczny K <= b - a + 1. Jeśli wygenerowany ciąg ma powtórzenia,
    zgłasza LFSRParameterError zamiast po cichu filtrować duplikaty.
    """
    validate_range_and_count(k, a, b)
    span = b - a + 1
    if k > span:
        raise LFSRParameterError(
            f"Niemożliwe wygenerowanie K={k} unikalnych liczb z przedziału [{a}, {b}] "
            f"(rozmiar przedziału wynosi tylko {span}, a wymagane jest K <= b - a + 1)."
        )
    gen = LFSR(length=length, taps=taps, seed=seed)
    seq = gen.generate_integers(k=k, a=a, b=b, bit_width=bit_width, mapping=mapping)
    stats = analyze_collisions(seq)
    if stats["total_collisions"] != 0:
        raise LFSRParameterError(
            f"Dla podanych parametrów wystąpiło {stats['total_collisions']} kolizji "
            f"(pierwsza na indeksie {stats['first_collision_index']})."
        )
    return seq


def save_numbers_to_file(
    filepath: str | Path,
    numbers: Iterable[int],
    header_comments: Sequence[str] | None = None,
) -> Path:
    """Zapisuje liczby całkowite do pliku tekstowego (po jednej w linii, opcjonalny nagłówek #)."""
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []
    if header_comments:
        for comment in header_comments:
            lines.append(f"# {comment}")
    for n in numbers:
        if isinstance(n, bool) or not isinstance(n, int):
            raise LFSRDataFormatError(f"Próba zapisu wartości niecałkowitej: {n!r}")
        lines.append(str(n))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def load_numbers_from_file(filepath: str | Path) -> list[int]:
    """Wczytuje liczby całkowite z pliku tekstowego z pełną kontrolą błędów."""
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Plik z liczbami nie istnieje: {path}")
    if not path.is_file():
        raise LFSRDataFormatError(f"Ścieżka nie jest plikiem: {path}")

    numbers: list[int] = []
    raw_lines = path.read_text(encoding="utf-8").splitlines()
    for line_no, raw in enumerate(raw_lines, start=1):
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            continue
        try:
            numbers.append(int(stripped))
        except ValueError as exc:
            raise LFSRDataFormatError(
                f"Błędny format danych w pliku {path}, linia {line_no}: {raw!r}"
            ) from exc

    if not numbers:
        raise LFSRDataFormatError(f"Plik {path} nie zawiera żadnych liczb całkowitych.")
    return numbers
