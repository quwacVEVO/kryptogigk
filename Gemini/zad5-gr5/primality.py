"""Moduł testów pierwszości i analizy statystycznej — Lab 05, Grupa 3 / Grupa 5.

Zawiera:
    1. Własną implementację szybkiego potęgowania binarnego modulo n (`mod_pow_binary`),
       bez korzystania z wbudowanego `pow(a, k, n)`.
    2. Prosty dokładny test dzielenia przez LICZBY PIERWSZE do floor(sqrt(n))
       (`trial_division_by_primes`) — zgodnie ze szczegółową treścią zadania Grupy 3.
    3. Niezależną metodę dokładną (`is_prime_exact_independent`, sprawdzanie 6k +/- 1)
       do niezależnej weryfikacji rzeczywistego statusu pierwszości (ground truth).
    4. Test Fermata dla losowo wybieranych podstaw (`fermat_test`).
    5. Test Millera–Rabina z konfigurowalną liczbą iteracji (`miller_rabin_test`).
    6. Narzędzia pomiarowe oparte o zegar monotoniczny `time.perf_counter_ns()`.
"""

from __future__ import annotations

import math
import random
import statistics
import time
from typing import Callable, Sequence


class PrimalityParameterError(ValueError):
    """Wyjątek zgłaszany przy niepoprawnych parametrach testu pierwszości."""


def mod_pow_binary(base: int, exp: int, mod: int) -> int:
    """Oblicza (base^exp) mod mod metodą szybkiego potęgowania binarnego (right-to-left).

    Nie wykorzystuje wbudowanego `pow(base, exp, mod)`.
    Złożoność czasowa: O(log(exp)) mnożeń modulo `mod`.
    """
    for name, val in (("base", base), ("exp", exp), ("mod", mod)):
        if isinstance(val, bool) or not isinstance(val, int):
            raise PrimalityParameterError(f"Argument {name} musi być liczbą całkowitą.")
    if exp < 0:
        raise PrimalityParameterError("Wykładnik `exp` musi być nieujemny.")
    if mod <= 0:
        raise PrimalityParameterError("Moduł `mod` musi być dodatnią liczbą całkowitą.")
    if mod == 1:
        return 0

    result = 1
    current_base = base % mod
    e = exp
    while e > 0:
        if e & 1:
            result = (result * current_base) % mod
        current_base = (current_base * current_base) % mod
        e >>= 1
    return result


def sieve_primes_up_to(limit: int) -> list[int]:
    """Wyznacza wszystkie liczby pierwsze <= limit za pomocą sita Eratostenesa."""
    if isinstance(limit, bool) or not isinstance(limit, int):
        raise PrimalityParameterError("Parametr `limit` musi być liczbą całkowitą.")
    if limit < 2:
        return []
    is_prime = bytearray(b"\x01") * (limit + 1)
    is_prime[0] = 0
    is_prime[1] = 0
    p = 2
    while p * p <= limit:
        if is_prime[p]:
            step = p
            start = p * p
            count = ((limit - start) // step) + 1
            is_prime[start : limit + 1 : step] = bytearray(count)
        p += 1
    return [i for i in range(2, limit + 1) if is_prime[i]]


def trial_division_by_primes(n: int, precomputed_primes: Sequence[int] | None = None) -> bool:
    """Dokładny test pierwszości przez dzielenie wyłącznie przez liczby pierwsze do floor(sqrt(n)).

    Jeśli `precomputed_primes` nie podano lub największa liczba pierwsza na liście
    jest mniejsza niż floor(sqrt(n)), funkcja sama wyznacza liczby pierwsze sitem Eratostenesa.
    """
    if isinstance(n, bool) or not isinstance(n, int):
        raise PrimalityParameterError("Testowana wartość n musi być liczbą całkowitą.")
    if n < 2:
        return False
    if n in (2, 3):
        return True
    if n % 2 == 0:
        return False

    limit = math.isqrt(n)
    if precomputed_primes is not None and (not precomputed_primes or precomputed_primes[-1] >= limit):
        primes = precomputed_primes
    else:
        primes = sieve_primes_up_to(limit)

    for p in primes:
        if p > limit:
            break
        if n % p == 0:
            return False
    return True


def is_prime_exact_independent(n: int) -> bool:
    """Niezależna, dokładna metoda deterministyczna (podzielność 6k +/- 1) bez sita.

    Służy jako niezależny wzorzec (ground truth) do weryfikacji testu dzielenia
    przez liczby pierwsze, testu Fermata oraz testu Millera–Rabina.
    """
    if isinstance(n, bool) or not isinstance(n, int):
        raise PrimalityParameterError("Testowana wartość n musi być liczbą całkowitą.")
    if n < 2:
        return False
    if n in (2, 3):
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    d = 5
    limit = math.isqrt(n)
    while d <= limit:
        if n % d == 0 or n % (d + 2) == 0:
            return False
        d += 6
    return True


def fermat_test(
    n: int,
    iterations: int = 10,
    rng: random.Random | None = None,
) -> bool:
    """Probabilistyczny test pierwszości Fermata (Małe Twierdzenie Fermata).

    Zwraca:
        - False: liczba n jest NA PEWNO złożona (lub n < 2).
        - True:  liczba n przeszła `iterations` losowych podstaw (prawdopodobnie pierwsza;
                 nie jest to dowód pierwszości — np. liczby Carmichaela mogą przejść test).
    """
    if isinstance(n, bool) or not isinstance(n, int):
        raise PrimalityParameterError("Testowana wartość n musi być liczbą całkowitą.")
    if isinstance(iterations, bool) or not isinstance(iterations, int) or iterations < 1:
        raise PrimalityParameterError("Liczba iteracji musi być liczbą całkowitą >= 1.")

    if n < 2:
        return False
    if n in (2, 3):
        return True
    if n % 2 == 0:
        return False

    generator = rng if rng is not None else random.Random()
    # Dla n >= 5 przedział dopuszczalnych podstaw to {2, 3, ..., n - 2}
    for _ in range(iterations):
        base = generator.randint(2, n - 2)
        if mod_pow_binary(base, n - 1, n) != 1:
            return False
    return True


def decompose_n_minus_1(n: int) -> tuple[int, int]:
    """Wyznacza u oraz nieparzyste r takie, że n - 1 = 2^u * r (dla nieparzystych n >= 3)."""
    if n < 3 or n % 2 == 0:
        raise PrimalityParameterError("Rozkład n - 1 = 2^u * r wymaga nieparzystego n >= 3.")
    u = 0
    r = n - 1
    while r % 2 == 0:
        r //= 2
        u += 1
    return u, r


def miller_rabin_test(
    n: int,
    iterations: int = 10,
    rng: random.Random | None = None,
) -> bool:
    """Probabilistyczny test pierwszości Millera–Rabina z własnym potęgowaniem binarnym.

    Zwraca:
        - False: liczba n jest NA PEWNO złożona (lub n < 2).
        - True:  liczba n przeszła `iterations` rund (prawdopodobnie pierwsza;
                 dla każdej liczby złożonej prawdopodobieństwo pomyłki <= 4^(-iterations)).
    """
    if isinstance(n, bool) or not isinstance(n, int):
        raise PrimalityParameterError("Testowana wartość n musi być liczbą całkowitą.")
    if isinstance(iterations, bool) or not isinstance(iterations, int) or iterations < 1:
        raise PrimalityParameterError("Liczba iteracji musi być liczbą całkowitą >= 1.")

    if n < 2:
        return False
    if n in (2, 3):
        return True
    if n % 2 == 0:
        return False

    u, r = decompose_n_minus_1(n)
    generator = rng if rng is not None else random.Random()

    for _ in range(iterations):
        t = generator.randint(2, n - 2)
        z = mod_pow_binary(t, r, n)
        if z == 1 or z == n - 1:
            continue
        witness_found = True
        for _ in range(u - 1):
            z = mod_pow_binary(z, 2, n)
            if z == n - 1:
                witness_found = False
                break
            if z == 1:
                return False
        if witness_found:
            return False
    return True


def summarize_timings_ns(timings_ns: Sequence[int]) -> dict[str, float | int]:
    """Oblicza statystyki czasu (min, max, średnia, mediana) w nanosekundach i mikrosekundach."""
    if not timings_ns:
        raise PrimalityParameterError("Lista pomiarów czasu nie może być pusta.")
    min_ns = min(timings_ns)
    max_ns = max(timings_ns)
    mean_ns = statistics.fmean(timings_ns)
    median_ns = statistics.median(timings_ns)
    total_ns = sum(timings_ns)
    return {
        "measurements": len(timings_ns),
        "min_ns": min_ns,
        "max_ns": max_ns,
        "mean_ns": round(mean_ns, 2),
        "median_ns": round(float(median_ns), 2),
        "total_ns": total_ns,
        "min_us": round(min_ns / 1_000.0, 3),
        "max_us": round(max_ns / 1_000.0, 3),
        "mean_us": round(mean_ns / 1_000.0, 3),
        "median_us": round(float(median_ns) / 1_000.0, 3),
        "total_ms": round(total_ns / 1_000_000.0, 3),
    }


def benchmark_primality_methods(
    numbers: Sequence[int],
    iterations: int = 10,
    rng_seed: int = 20261126,
    source_label: str = "dataset",
) -> dict[str, object]:
    """Uruchamia wszystkie trzy testy pierwszości na podanej liście liczb z pomiarem czasu.

    Uwaga metodyczna:
        - Każdy pomiar obejmuje pojedyncze wywołanie testu na jednej pozycji z listy wejściowej
          (bez czasu wczytywania pliku).
        - Dla testu dzielenia przez liczby pierwsze raportujemy zarówno czas z prekomputacją
          sita Eratostenesa do floor(sqrt(max(numbers))) (osobno podając czas budowy sita),
          jak i wariant pełny bez współdzielonego sita w analizie skalowania.
        - Status rzeczywisty (`ground_truth`) wyznaczamy niezależną metodą `is_prime_exact_independent`.
    """
    if not numbers:
        raise PrimalityParameterError("Lista liczb do testowania nie może być pusta.")

    max_val = max(numbers)
    sieve_limit = math.isqrt(max_val) if max_val >= 2 else 0
    t_sieve_start = time.perf_counter_ns()
    shared_primes = sieve_primes_up_to(sieve_limit)
    sieve_build_ns = time.perf_counter_ns() - t_sieve_start

    # Niezależny status rzeczywisty (poza pomiarem porównywanych 3 testów)
    ground_truth = [is_prime_exact_independent(n) for n in numbers]
    true_primes_count = sum(1 for x in ground_truth if x)
    true_composites_count = len(numbers) - true_primes_count

    rng_fermat = random.Random(rng_seed)
    rng_mr = random.Random(rng_seed)

    methods: list[tuple[str, Callable[[int], bool]]] = [
        ("trial_division_primes", lambda x: trial_division_by_primes(x, shared_primes)),
        ("fermat", lambda x: fermat_test(x, iterations=iterations, rng=rng_fermat)),
        ("miller_rabin", lambda x: miller_rabin_test(x, iterations=iterations, rng=rng_mr)),
    ]

    per_item_records: list[dict[str, object]] = [
        {
            "index": idx,
            "number": n,
            "actual_prime": ground_truth[idx],
        }
        for idx, n in enumerate(numbers)
    ]

    summaries: dict[str, dict[str, object]] = {}

    for method_name, fn in methods:
        timings_ns: list[int] = []
        pseudoprimes = 0  # złożona uznana za pierwszą (false positive)
        pseudocomposites = 0  # pierwsza uznana za złożoną (false negative)
        predicted_primes = 0

        for idx, n in enumerate(numbers):
            t0 = time.perf_counter_ns()
            verdict = fn(n)
            elapsed = time.perf_counter_ns() - t0
            timings_ns.append(elapsed)

            if verdict:
                predicted_primes += 1
            actual = ground_truth[idx]
            if verdict and not actual:
                pseudoprimes += 1
            elif (not verdict) and actual:
                pseudocomposites += 1

            per_item_records[idx][f"{method_name}_prime"] = verdict
            per_item_records[idx][f"{method_name}_ns"] = elapsed

        stats = summarize_timings_ns(timings_ns)
        total_errors = pseudoprimes + pseudocomposites
        accuracy_pct = ((len(numbers) - total_errors) / len(numbers)) * 100.0
        summaries[method_name] = {
            **stats,
            "predicted_primes": predicted_primes,
            "pseudoprimes_fp": pseudoprimes,
            "pseudocomposites_fn": pseudocomposites,
            "total_errors": total_errors,
            "accuracy_pct": round(accuracy_pct, 4),
        }

    return {
        "source": source_label,
        "count": len(numbers),
        "unique_count": len(set(numbers)),
        "min_value": min(numbers),
        "max_value": max_val,
        "iterations": iterations,
        "rng_seed": rng_seed,
        "true_primes": true_primes_count,
        "true_composites": true_composites_count,
        "sieve_limit": sieve_limit,
        "sieve_primes_count": len(shared_primes),
        "sieve_build_ns": sieve_build_ns,
        "sieve_build_us": round(sieve_build_ns / 1_000.0, 3),
        "summaries": summaries,
        "records": per_item_records,
    }
