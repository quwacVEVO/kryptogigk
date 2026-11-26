"""Testy pierwszości (zakres grupy 3).

Zawiera:
  * `trial_division_is_prime` - dokładny test dzielenia przez LICZBY PIERWSZE do floor(sqrt(n)),
  * `pow_mod`                 - własne szybkie potęgowanie binarne modulo n (wg notatki, pot_mod2),
  * `fermat_is_probably_prime`- test Fermata z losowanymi podstawami (wg notatki, pierwszaF),
  * `miller_rabin_is_probably_prime` - test Millera-Rabina (wg notatki, pierwszaMR).

Uwaga metodologiczna: Fermat i Miller-Rabin NIE dowodzą pierwszości. Zwracają
"prawdopodobnie pierwsza" (True) albo "złożona" (False, decyzja pewna, bo oparta
na kontrprzykładzie). Jedynym dokładnym testem w tym module jest dzielenie próbne
i tylko ono jest używane jako podstawa odniesienia (rzeczywisty status pierwszości).

Wbudowana funkcja `pow` nie jest używana w testach - służy wyłącznie jako
NIEZALEŻNA KONTROLA poprawności `pow_mod` w pliku test_primality.py.
"""

import argparse
import random
from math import isqrt

# Liczby Carmichaela - złożone, które dla każdej podstawy względnie pierwszej z n
# spełniają małe twierdzenie Fermata, więc potrafią zmylić test Fermata.
KNOWN_CARMICHAEL = (561, 1105, 1729, 2465, 2821, 6601, 8911, 10585, 15841, 29341)

# Pamięć na liczby pierwsze dla testu dzielenia (sito rozszerzane w miarę potrzeby).
_PRIME_CACHE = [2, 3]
_PRIME_CACHE_LIMIT = 3


def primes_up_to(limit):
    """Lista liczb pierwszych <= limit (sito Eratostenesa, własna implementacja)."""
    if limit < 2:
        return []
    sieve = bytearray([1]) * (limit + 1)
    sieve[0] = sieve[1] = 0
    for number in range(2, isqrt(limit) + 1):
        if sieve[number]:
            sieve[number * number::number] = bytearray(len(sieve[number * number::number]))
    return [number for number in range(limit + 1) if sieve[number]]


def prepare_primes(limit):
    """Przygotowuje (i zapamiętuje) listę liczb pierwszych do `limit`.

    Wywoływana jawnie PRZED pomiarami czasu, żeby mierzony czas testu dzielenia
    nie zawierał budowy sita. Bez tego pierwsze wywołanie testu byłoby
    nieporównywalnie dłuższe od pozostałych.
    """
    global _PRIME_CACHE, _PRIME_CACHE_LIMIT
    if limit > _PRIME_CACHE_LIMIT:
        _PRIME_CACHE = primes_up_to(limit)
        _PRIME_CACHE_LIMIT = limit
    return len(_PRIME_CACHE)


def trial_division_is_prime(n):
    """Dokładny test pierwszości: dzielenie przez liczby pierwsze <= floor(sqrt(n)).

    Wersja z notatki dzieli przez wszystkie liczby naturalne; treść zadania
    wymaga dzielenia przez liczby pierwsze, co zmniejsza liczbę dzieleń
    z ~sqrt(n) do ~sqrt(n)/ln(sqrt(n)).
    """
    if n < 2:
        return False
    root = isqrt(n)
    prepare_primes(root)
    for prime in _PRIME_CACHE:
        if prime > root:
            break
        if n % prime == 0:
            return n == prime
    return True


def pow_mod(base, exponent, modulus):
    """Szybkie potęgowanie binarne: base^exponent mod modulus.

    Implementacja wg notatki (pot_mod2): przebieg po bitach wykładnika OD
    NAJSTARSZEGO, w każdym kroku podniesienie do kwadratu, a przy bicie 1
    dodatkowe mnożenie przez podstawę.
    """
    if modulus <= 0:
        raise ValueError("moduł musi być dodatni, jest {}".format(modulus))
    if exponent < 0:
        raise ValueError("wykładnik nie może być ujemny, jest {}".format(exponent))
    base %= modulus
    result = 1
    for bit in bin(exponent)[2:]:
        result = (result * result) % modulus
        if bit == "1":
            result = (result * base) % modulus
    return result


def decompose(n):
    """Rozkład n - 1 = 2^u * r z nieparzystym r (funkcja `ur` z notatki)."""
    if n < 2:
        raise ValueError("rozkład n-1 = 2^u * r wymaga n >= 2")
    u = 0
    r = n - 1
    while r % 2 == 0:
        r //= 2
        u += 1
    return u, r


def _trivial_case(n):
    """Wspólna obsługa przypadków brzegowych z notatki (slajd "Uwagi").

    Zwraca True/False, gdy odpowiedź jest pewna bez losowania, albo None,
    gdy trzeba wykonać właściwy test (n >= 5 i nieparzyste).
    """
    if n < 2:
        return False
    if n in (2, 3):
        return True
    if n % 2 == 0:
        return False
    return None


def fermat_is_probably_prime(n, rounds=5, rng=None):
    """Test Fermata: `rounds` losowych podstaw t z {2, ..., n-2}.

    Zwraca False (liczba złożona - pewne) lub True (prawdopodobnie pierwsza).
    Liczby Carmichaela przechodzą ten test dla prawie wszystkich podstaw.
    """
    if rounds < 1:
        raise ValueError("liczba iteracji musi być >= 1, jest {}".format(rounds))
    trivial = _trivial_case(n)
    if trivial is not None:
        return trivial
    generator = rng if rng is not None else random.Random()
    for _ in range(rounds):
        base = generator.randint(2, n - 2)  # n >= 5, więc zakres jest niepusty
        if pow_mod(base, n - 1, n) != 1:
            return False
    return True


def miller_rabin_is_probably_prime(n, rounds=5, rng=None):
    """Test Millera-Rabina z ustaloną liczbą iteracji (pseudokod `pierwszaMR` z notatki).

    Dla n złożonego prawdopodobieństwo błędnego uznania za pierwszą jest
    <= 4^(-rounds); dla n pierwszego test nigdy nie zwraca False.
    """
    if rounds < 1:
        raise ValueError("liczba iteracji musi być >= 1, jest {}".format(rounds))
    trivial = _trivial_case(n)
    if trivial is not None:
        return trivial
    generator = rng if rng is not None else random.Random()
    u, r = decompose(n)
    for _ in range(rounds):
        base = generator.randint(2, n - 2)
        value = pow_mod(base, r, n)
        if value == 1:
            continue
        squarings = 0
        while value != n - 1:
            value = (value * value) % n
            squarings += 1
            if value == 1 or squarings == u:
                return False
    return True


def main(argv=None):
    parser = argparse.ArgumentParser(description="Testy pierwszości dla podanych liczb.")
    parser.add_argument("numbers", nargs="+", type=int, help="liczby do sprawdzenia")
    parser.add_argument("--rounds", type=int, default=5, help="liczba iteracji testów probabilistycznych")
    parser.add_argument("--seed", type=int, default=12345, help="ziarno losowania podstaw")
    args = parser.parse_args(argv)

    rng = random.Random(args.seed)
    print("n\tdzielenie\tFermat(s={0})\tMiller-Rabin(s={0})".format(args.rounds))
    for n in args.numbers:
        exact = trial_division_is_prime(n)
        fermat = fermat_is_probably_prime(n, args.rounds, rng)
        miller = miller_rabin_is_probably_prime(n, args.rounds, rng)
        print("{}\t{}\t{}\t{}".format(n, exact, fermat, miller))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
