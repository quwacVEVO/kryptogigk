"""Dokładny i probabilistyczne testy pierwszości wymagane w laboratorium."""

from __future__ import annotations

from math import gcd, isqrt
from random import Random


def primes_up_to(limit: int) -> list[int]:
    """Wyznacz liczby pierwsze do ``limit`` prostym sitem Eratostenesa."""

    if limit < 2:
        return []
    sieve = bytearray(b"\x01") * (limit + 1)
    sieve[0:2] = b"\x00\x00"
    for candidate in range(2, isqrt(limit) + 1):
        if sieve[candidate]:
            start = candidate * candidate
            sieve[start : limit + 1 : candidate] = b"\x00" * (
                (limit - start) // candidate + 1
            )
    return [value for value, flag in enumerate(sieve) if flag]


def prime_division_test(number: int) -> bool:
    """Dokładny test przez dzielenie wyłącznie przez liczby pierwsze do sqrt(n)."""

    if not isinstance(number, int):
        raise TypeError("Testowana wartość musi być liczbą całkowitą.")
    if number < 2:
        return False
    for prime in primes_up_to(isqrt(number)):
        if number % prime == 0:
            return number == prime
    return True


def mod_pow_binary(base: int, exponent: int, modulus: int) -> int:
    """Oblicz ``base**exponent mod modulus`` metodą square-and-multiply."""

    if not all(isinstance(value, int) for value in (base, exponent, modulus)):
        raise TypeError("Podstawa, wykładnik i moduł muszą być całkowite.")
    if exponent < 0:
        raise ValueError("Wykładnik nie może być ujemny.")
    if modulus <= 0:
        raise ValueError("Moduł musi być dodatni.")
    result = 1 % modulus
    factor = base % modulus
    power = exponent
    while power:
        if power & 1:
            result = (result * factor) % modulus
        factor = (factor * factor) % modulus
        power >>= 1
    return result


def _validate_iterations(iterations: int) -> None:
    if not isinstance(iterations, int) or iterations <= 0:
        raise ValueError("Liczba iteracji musi być dodatnią liczbą całkowitą.")


def fermat_test(number: int, iterations: int, rng: Random) -> bool:
    """Test Fermata; wynik True oznacza jedynie 'prawdopodobnie pierwsza'."""

    _validate_iterations(iterations)
    if number < 2:
        return False
    if number in (2, 3):
        return True
    if number % 2 == 0:
        return False
    for _ in range(iterations):
        base = rng.randrange(2, number - 1)
        if gcd(base, number) != 1:
            return False
        if mod_pow_binary(base, number - 1, number) != 1:
            return False
    return True


def _decompose_number_minus_one(number: int) -> tuple[int, int]:
    exponent_of_two = 0
    odd_part = number - 1
    while odd_part % 2 == 0:
        odd_part //= 2
        exponent_of_two += 1
    return exponent_of_two, odd_part


def miller_rabin_test(number: int, iterations: int, rng: Random) -> bool:
    """Probabilistyczny test Millera-Rabina z losowanymi podstawami."""

    _validate_iterations(iterations)
    if number < 2:
        return False
    if number in (2, 3):
        return True
    if number % 2 == 0:
        return False

    power_of_two, odd_part = _decompose_number_minus_one(number)
    for _ in range(iterations):
        base = rng.randrange(2, number - 1)
        value = mod_pow_binary(base, odd_part, number)
        if value in (1, number - 1):
            continue
        for _ in range(power_of_two - 1):
            value = (value * value) % number
            if value == number - 1:
                break
            if value == 1:
                return False
        else:
            return False
    return True
