import random
import unittest

from lab05.primality import (
    fermat_test,
    miller_rabin_test,
    mod_pow_binary,
    prime_division_test,
)


class FixedBaseRNG:
    def __init__(self, base):
        self.base = base

    def randrange(self, start, stop):
        if not start <= self.base < stop:
            raise AssertionError("Ustalona podstawa jest poza żądanym zakresem.")
        return self.base


class ModularExponentiationTests(unittest.TestCase):
    def test_example_from_theory(self):
        self.assertEqual(mod_pow_binary(5, 100, 22), 1)

    def test_matches_python_reference(self):
        rng = random.Random(20261122)
        for _ in range(500):
            base = rng.randrange(-10_000, 10_001)
            exponent = rng.randrange(0, 500)
            modulus = rng.randrange(1, 2_000)
            self.assertEqual(
                mod_pow_binary(base, exponent, modulus),
                pow(base, exponent, modulus),
            )

    def test_invalid_parameters(self):
        with self.assertRaises(ValueError):
            mod_pow_binary(2, -1, 5)
        with self.assertRaises(ValueError):
            mod_pow_binary(2, 3, 0)


class PrimalityTests(unittest.TestCase):
    def test_edge_cases_and_known_values(self):
        expected = {
            0: False,
            1: False,
            2: True,
            3: True,
            4: False,
            5: True,
            9: False,
            25: False,
            97: True,
            221: False,
            9973: True,
        }
        for number, truth in expected.items():
            with self.subTest(number=number):
                self.assertEqual(prime_division_test(number), truth)
                self.assertEqual(fermat_test(number, 5, random.Random(123)), truth)
                self.assertEqual(miller_rabin_test(number, 5, random.Random(123)), truth)

    def test_fermat_can_be_fooled_by_carmichael_number(self):
        self.assertFalse(prime_division_test(561))
        self.assertTrue(fermat_test(561, 1, FixedBaseRNG(2)))

    def test_miller_rabin_rejects_same_carmichael_number(self):
        self.assertFalse(miller_rabin_test(561, 1, FixedBaseRNG(2)))

    def test_no_false_composites_for_known_primes(self):
        primes = [2, 3, 5, 7, 11, 97, 101, 1009, 7919]
        for number in primes:
            self.assertTrue(fermat_test(number, 10, random.Random(number)))
            self.assertTrue(miller_rabin_test(number, 10, random.Random(number)))


if __name__ == "__main__":
    unittest.main()
