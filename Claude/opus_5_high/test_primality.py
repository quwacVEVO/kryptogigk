"""Testy poprawności testów pierwszości i potęgowania modulo.

Odniesienie: notatka "Kryptologia lab05", slajdy 8-14 (pierwsza, pierwszaF,
pierwszaMR, ur, pot_mod2 i przykład 5^100 mod 22).
"""

import random
import unittest

import params
from primality import (KNOWN_CARMICHAEL, decompose, fermat_is_probably_prime,
                       miller_rabin_is_probably_prime, pow_mod, prepare_primes, primes_up_to,
                       trial_division_is_prime)

PIERWSZE_DO_100 = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47,
                   53, 59, 61, 67, 71, 73, 79, 83, 89, 97]


class TestPotegowanieModulo(unittest.TestCase):
    def test_przyklad_z_notatki(self):
        # Notatka, slajd 13: 5^100 mod 22 = 1
        self.assertEqual(pow_mod(5, 100, 22), 1)

    def test_zgodnosc_z_wbudowanym_pow(self):
        """Niezależna kontrola: wbudowane `pow` używane TYLKO tutaj, nie w testach."""
        rng = random.Random(20261125)
        for _ in range(5000):
            base = rng.randrange(0, 10 ** 7)
            exponent = rng.randrange(0, 10 ** 5)
            modulus = rng.randrange(1, 10 ** 7)
            self.assertEqual(pow_mod(base, exponent, modulus), pow(base, exponent, modulus))

    def test_duze_liczby(self):
        self.assertEqual(pow_mod(123456789, 987654321, 2 ** 61 - 1),
                         pow(123456789, 987654321, 2 ** 61 - 1))

    def test_przypadki_brzegowe(self):
        self.assertEqual(pow_mod(7, 0, 13), 1)
        self.assertEqual(pow_mod(0, 5, 13), 0)
        self.assertEqual(pow_mod(0, 0, 13), 1)
        self.assertEqual(pow_mod(5, 3, 1), 0)
        self.assertEqual(pow_mod(10 ** 9, 1, 7), 10 ** 9 % 7)

    def test_bledne_argumenty(self):
        with self.assertRaises(ValueError):
            pow_mod(2, 10, 0)
        with self.assertRaises(ValueError):
            pow_mod(2, 10, -5)
        with self.assertRaises(ValueError):
            pow_mod(2, -1, 7)


class TestRozkladNMinusJeden(unittest.TestCase):
    def test_rozklad_jest_poprawny(self):
        for n in range(2, 2000):
            u, r = decompose(n)
            self.assertEqual(2 ** u * r, n - 1)
            self.assertTrue(r % 2 == 1 or n == 2)

    def test_przyklad_561(self):
        # 560 = 2^4 * 35
        self.assertEqual(decompose(561), (4, 35))

    def test_zbyt_mala_liczba(self):
        with self.assertRaises(ValueError):
            decompose(1)


class TestSitoIDzielenieProbne(unittest.TestCase):
    def test_sito_dla_malych_limitow(self):
        self.assertEqual(primes_up_to(100), PIERWSZE_DO_100)
        self.assertEqual(primes_up_to(1), [])
        self.assertEqual(primes_up_to(2), [2])

    def test_liczba_liczb_pierwszych_do_miliona(self):
        # Znana wartość: pi(10^6) = 78498
        self.assertEqual(len(primes_up_to(10 ** 6)), 78498)

    def test_dzielenie_probne_na_malych_liczbach(self):
        for n in range(-10, 101):
            with self.subTest(n=n):
                self.assertEqual(trial_division_is_prime(n), n in PIERWSZE_DO_100)

    def test_dzielenie_probne_zgodne_z_sitem_do_20000(self):
        prime_set = set(primes_up_to(20000))
        for n in range(0, 20001):
            if trial_division_is_prime(n) != (n in prime_set):
                self.fail("niezgodność dla n = {}".format(n))

    def test_kwadraty_liczb_pierwszych_sa_zlozone(self):
        for prime in (2, 3, 5, 7, 31, 997, 7919):
            self.assertFalse(trial_division_is_prime(prime * prime))

    def test_duze_liczby_pierwsze(self):
        for prime in (104729, 1000003, 15485863, 2 ** 31 - 1):
            self.assertTrue(trial_division_is_prime(prime))

    def test_duze_liczby_zlozone(self):
        self.assertFalse(trial_division_is_prime(1000001))        # 101 * 9901
        self.assertFalse(trial_division_is_prime(104729 * 104723))

    def test_prepare_primes_nie_zmienia_wynikow(self):
        prepare_primes(1000)
        self.assertTrue(trial_division_is_prime(999983))
        prepare_primes(10)
        self.assertTrue(trial_division_is_prime(999983))


class TestPrzypadkiBrzegoweTestow(unittest.TestCase):
    """Warunki z notatki: a = 1 -> złożona, a = 2 lub 3 -> pierwsza, a parzyste -> złożona."""

    def setUp(self):
        self.rng = random.Random(params.RNG_SEED)

    def test_liczby_mniejsze_od_dwoch(self):
        for n in (-100, -1, 0, 1):
            with self.subTest(n=n):
                self.assertFalse(fermat_is_probably_prime(n, 5, self.rng))
                self.assertFalse(miller_rabin_is_probably_prime(n, 5, self.rng))
                self.assertFalse(trial_division_is_prime(n))

    def test_dwa_i_trzy(self):
        for n in (2, 3):
            self.assertTrue(fermat_is_probably_prime(n, 5, self.rng))
            self.assertTrue(miller_rabin_is_probably_prime(n, 5, self.rng))

    def test_liczby_parzyste(self):
        for n in (4, 6, 8, 100, 10 ** 9):
            with self.subTest(n=n):
                self.assertFalse(fermat_is_probably_prime(n, 5, self.rng))
                self.assertFalse(miller_rabin_is_probably_prime(n, 5, self.rng))

    def test_najmniejsze_nieparzyste_przypadki(self):
        self.assertTrue(fermat_is_probably_prime(5, 5, self.rng))
        self.assertTrue(miller_rabin_is_probably_prime(5, 5, self.rng))
        self.assertFalse(fermat_is_probably_prime(9, 5, self.rng))
        self.assertFalse(miller_rabin_is_probably_prime(9, 5, self.rng))

    def test_zerowa_liczba_iteracji_jest_bledem(self):
        with self.assertRaises(ValueError):
            fermat_is_probably_prime(97, 0)
        with self.assertRaises(ValueError):
            miller_rabin_is_probably_prime(97, 0)


class TestZadnaLiczbaPierwszaNieJestOdrzucana(unittest.TestCase):
    """Oba testy nie mogą odrzucić liczby pierwszej - to własność, nie przypadek."""

    def test_fermat_akceptuje_wszystkie_liczby_pierwsze_do_5000(self):
        rng = random.Random(params.RNG_SEED)
        for prime in primes_up_to(5000):
            if not fermat_is_probably_prime(prime, 5, rng):
                self.fail("test Fermata odrzucił liczbę pierwszą {}".format(prime))

    def test_miller_rabin_akceptuje_wszystkie_liczby_pierwsze_do_5000(self):
        rng = random.Random(params.RNG_SEED)
        for prime in primes_up_to(5000):
            if not miller_rabin_is_probably_prime(prime, 5, rng):
                self.fail("test Millera-Rabina odrzucił liczbę pierwszą {}".format(prime))

    def test_duze_liczby_pierwsze_przechodza_oba_testy(self):
        rng = random.Random(params.RNG_SEED)
        for prime in (104729, 1000003, 2 ** 31 - 1, 2 ** 61 - 1):
            with self.subTest(prime=prime):
                self.assertTrue(fermat_is_probably_prime(prime, 10, rng))
                self.assertTrue(miller_rabin_is_probably_prime(prime, 10, rng))


class TestLiczbyMylaceTestFermata(unittest.TestCase):
    def test_liczby_carmichaela_sa_zlozone(self):
        for n in KNOWN_CARMICHAEL:
            self.assertFalse(trial_division_is_prime(n))

    def test_podstawa_2_myli_fermata_dla_341_i_561(self):
        # 341 = 11 * 31 (pseudopierwsza Fermata przy podstawie 2), 561 = 3 * 11 * 17 (Carmichael)
        self.assertEqual(pow_mod(2, 340, 341), 1)
        self.assertEqual(pow_mod(2, 560, 561), 1)

    def test_miller_rabin_wykrywa_te_liczby_dla_podstawy_2(self):
        for n in (341, 561):
            with self.subTest(n=n):
                u, r = decompose(n)
                value = pow_mod(2, r, n)
                sequence = [value]
                for _ in range(u):
                    value = (value * value) % n
                    sequence.append(value)
                # Brak -1 w ciągu, a na końcu 1 => świadek złożoności
                self.assertNotIn(n - 1, sequence)
                self.assertEqual(sequence[-1], 1)

    def test_wiekszosc_podstaw_myli_fermata_dla_561(self):
        liars = [t for t in range(2, 560) if pow_mod(t, 560, 561) == 1]
        # Dla liczby Carmichaela kłamcami są wszystkie podstawy względnie pierwsze z n.
        # phi(561) = phi(3)*phi(11)*phi(17) = 2*10*16 = 320, bez podstaw 1 i 560 => 318.
        self.assertEqual(len(liars), 318)
        self.assertGreater(len(liars) / 558, 0.5)

    def test_miller_rabin_ma_duzo_mniej_klamcow_niz_fermat(self):
        fermat_liars = sum(1 for t in range(2, 560) if pow_mod(t, 560, 561) == 1)
        mr_liars = 0
        u, r = decompose(561)
        for t in range(2, 560):
            value = pow_mod(t, r, 561)
            if value == 1:
                mr_liars += 1
                continue
            passed = True
            squarings = 0
            while value != 560:
                value = (value * value) % 561
                squarings += 1
                if value == 1 or squarings == u:
                    passed = False
                    break
            if passed:
                mr_liars += 1
        self.assertLess(mr_liars * 10, fermat_liars)


class TestZgodnoscZDokladnymTestem(unittest.TestCase):
    def test_miller_rabin_s20_jest_dokladny_do_3000(self):
        rng = random.Random(params.RNG_SEED)
        for n in range(2, 3001):
            if miller_rabin_is_probably_prime(n, 20, rng) != trial_division_is_prime(n):
                self.fail("niezgodność dla n = {}".format(n))

    def test_fermat_moze_sie_mylic_tylko_w_jedna_strone(self):
        rng = random.Random(params.RNG_SEED)
        for n in range(2, 3001):
            decision = fermat_is_probably_prime(n, 1, rng)
            if trial_division_is_prime(n):
                self.assertTrue(decision, "odrzucona liczba pierwsza {}".format(n))


class TestOdtwarzalnosc(unittest.TestCase):
    def test_to_samo_ziarno_daje_te_same_decyzje(self):
        numbers = list(range(500, 600))
        first = [fermat_is_probably_prime(n, 3, random.Random(params.RNG_SEED)) for n in numbers]
        second = [fermat_is_probably_prime(n, 3, random.Random(params.RNG_SEED)) for n in numbers]
        self.assertEqual(first, second)

    def test_decyzje_dla_liczb_zlozonych_moga_zalezec_od_ziarna(self):
        # 561 (Carmichael): przy jednej iteracji wynik zależy od wylosowanej podstawy.
        results = {fermat_is_probably_prime(561, 1, random.Random(seed)) for seed in range(50)}
        self.assertEqual(results, {True, False})


if __name__ == "__main__":
    unittest.main()
