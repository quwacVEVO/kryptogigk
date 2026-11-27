"""Pakiet testów poprawności dla Lab 05 (Grupa 5: LFSR, LCG, Testy pierwszości).

Uruchomienie:
    python3 -m unittest discover -s zad5-gr5/tests -v
"""

from __future__ import annotations

import math
import random
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import lcg
import lfsr
import primality


class TestLFSR(unittest.TestCase):
    """Testy poprawności generatora LFSR (Grupa 1)."""

    def test_known_first_steps_from_lecture_notes(self) -> None:
        # Przykład 1 ze slajdu 6/14: p = (1, 1, 0), S = (0, 0, 1)
        # S0=0, S1=0, S2=1, S3=0, S4=1, S5=1, S6=1, a następnie powtórzenie okresu 7
        gen = lfsr.LFSR.from_coefficients([1, 1, 0], [0, 0, 1])
        bits = gen.generate_bits(14)
        self.assertEqual(bits, [0, 0, 1, 0, 1, 1, 1, 0, 0, 1, 0, 1, 1, 1])

    def test_lecture_example_4_bit_maximal_cycle(self) -> None:
        # Przykład 2 ze slajdu 6/14: p = (1, 1, 0, 0), S = (0, 0, 0, 1), wielomian pierwotny x^4+x+1
        cyc = lfsr.detect_state_cycle(length=4, taps=(0, 1), seed=(0, 0, 0, 1))
        self.assertTrue(cyc["found"])
        self.assertEqual(cyc["preperiod"], 0)
        self.assertEqual(cyc["cycle_length"], 15)
        self.assertTrue(cyc["is_maximal"])

    def test_lecture_example_non_primitive_short_cycle(self) -> None:
        # Przykład 3 ze slajdu 6/14: p = (1, 1, 1, 1), S = (1, 0, 0, 1) -> cykl 5 (< 15)
        cyc = lfsr.detect_state_cycle(length=4, taps=(0, 1, 2, 3), seed=(1, 0, 0, 1))
        self.assertTrue(cyc["found"])
        self.assertEqual(cyc["cycle_length"], 5)
        self.assertFalse(cyc["is_maximal"])

    def test_zero_seed_rejected_by_default_and_cycle_1_when_allowed(self) -> None:
        with self.assertRaises(lfsr.LFSRParameterError):
            lfsr.LFSR(length=4, taps=(0, 1), seed=(0, 0, 0, 0))
        cyc = lfsr.detect_state_cycle(
            length=4, taps=(0, 1), seed=(0, 0, 0, 0), allow_zero_seed=True
        )
        self.assertEqual(cyc["cycle_length"], 1)
        self.assertEqual(cyc["preperiod"], 0)

    def test_invalid_parameters_raise_errors(self) -> None:
        with self.assertRaises(lfsr.LFSRParameterError):
            lfsr.LFSR(length=1, taps=(0,), seed=(1,))
        with self.assertRaises(lfsr.LFSRParameterError):
            lfsr.LFSR(length=4, taps=(0, 4), seed=(1, 0, 0, 0))
        with self.assertRaises(lfsr.LFSRParameterError):
            lfsr.LFSR(length=4, taps=(0, 0), seed=(1, 0, 0, 0))
        with self.assertRaises(lfsr.LFSRParameterError):
            lfsr.LFSR(length=4, taps=(0, 1), seed=(1, 0, 2, 0))
        with self.assertRaises(lfsr.LFSRParameterError):
            gen = lfsr.LFSR(length=4, taps=(0, 1), seed=(1, 0, 0, 1))
            gen.generate_integers(k=5, a=100, b=50)

    def test_range_bounds_and_collision_free_example(self) -> None:
        # n=17, taps=(0, 3) -> wielomian pierwotny x^17 + x^3 + 1, okres 131071
        seed17 = (1, 0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 1, 0, 1, 0, 0, 1)
        seq = lfsr.generate_collision_free_sequence(
            k=200, a=1000, b=100000, length=17, taps=(0, 3), seed=seed17, mapping="rejection"
        )
        self.assertEqual(len(seq), 200)
        self.assertEqual(len(set(seq)), 200)
        self.assertTrue(all(1000 <= x <= 100000 for x in seq))

    def test_impossible_collision_free_range_rejected(self) -> None:
        seed8 = (1, 0, 1, 0, 0, 1, 1, 0)
        with self.assertRaises(lfsr.LFSRParameterError):
            lfsr.generate_collision_free_sequence(
                k=20, a=1, b=10, length=8, taps=(0, 2, 3, 4), seed=seed8
            )

    def test_file_io_and_error_handling(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "lfsr_test.txt"
            lfsr.save_numbers_to_file(path, [10, 20, 30], header_comments=["Nagłówek"])
            loaded = lfsr.load_numbers_from_file(path)
            self.assertEqual(loaded, [10, 20, 30])

            missing = Path(tmpdir) / "brak.txt"
            with self.assertRaises(FileNotFoundError):
                lfsr.load_numbers_from_file(missing)

            bad = Path(tmpdir) / "bad.txt"
            bad.write_text("123\nnie_liczba\n456\n", encoding="utf-8")
            with self.assertRaises(lfsr.LFSRDataFormatError):
                lfsr.load_numbers_from_file(bad)

            empty = Path(tmpdir) / "empty.txt"
            empty.write_text("# tylko komentarz\n\n", encoding="utf-8")
            with self.assertRaises(lfsr.LFSRDataFormatError):
                lfsr.load_numbers_from_file(empty)


class TestLCG(unittest.TestCase):
    """Testy poprawności generatora LCG (Grupa 2)."""

    def test_known_steps_from_lecture_notes(self) -> None:
        # Slajd 3/14: lcg(a=8121, c=28411, m=134456, x0=55)
        gen = lcg.LCG(m=134456, a=8121, c=28411, x0=55)
        x1 = gen.next_state()
        x2 = gen.next_state()
        self.assertEqual(x1, (8121 * 55 + 28411) % 134456)
        self.assertEqual(x2, (8121 * x1 + 28411) % 134456)

    def test_hull_dobell_and_cycle_detection(self) -> None:
        # Slajd 3/14: m=134456, a=8121, c=28411 ma okres maksymalny 134456
        info = lcg.detect_state_cycle(m=134456, a=8121, c=28411, x0=55, max_steps=200_000)
        self.assertTrue(info["measured"])
        self.assertEqual(info["preperiod"], 0)
        self.assertEqual(info["cycle_length"], 134456)
        self.assertTrue(info["hull_dobell"]["has_maximal_period_m"])

        # Przypadek z częścią przedcykliczną mu > 0: m=16, a=2, c=1, x0=0
        # 0 -> 1 -> 3 -> 7 -> 15 -> 15 -> 15 (mu=4, lambda=1)
        pre = lcg.detect_state_cycle(m=16, a=2, c=1, x0=0)
        self.assertTrue(pre["measured"])
        self.assertEqual(pre["preperiod"], 4)
        self.assertEqual(pre["cycle_length"], 1)
        self.assertFalse(pre["hull_dobell"]["has_maximal_period_m"])

    def test_range_bounds_and_collision_free_lcg(self) -> None:
        seq = lcg.generate_collision_free_sequence(
            k=200,
            low=1000,
            high=100000,
            m=2**31,
            a=1103515245,
            c=12345,
            x0=123456,
            mapping="scale",
        )
        self.assertEqual(len(seq), 200)
        self.assertEqual(len(set(seq)), 200)
        self.assertTrue(all(1000 <= x <= 100000 for x in seq))

    def test_invalid_params_and_file_errors(self) -> None:
        with self.assertRaises(lcg.LCGParameterError):
            lcg.LCG(m=1, a=5, c=1, x0=0)
        with self.assertRaises(lcg.LCGParameterError):
            lcg.LCG(m=100, a=0, c=1, x0=0)
        with self.assertRaises(lcg.LCGParameterError):
            lcg.LCG(m=100, a=5, c=-1, x0=0)
        with self.assertRaises(lcg.LCGParameterError):
            lcg.generate_collision_free_sequence(
                k=15, low=1, high=10, m=134456, a=8121, c=28411, x0=55
            )
        with tempfile.TemporaryDirectory() as tmpdir:
            missing = Path(tmpdir) / "missing_lcg.txt"
            with self.assertRaises(FileNotFoundError):
                lcg.load_numbers_from_file(missing)
            bad = Path(tmpdir) / "bad_lcg.txt"
            bad.write_text("42\n3.14\n", encoding="utf-8")
            with self.assertRaises(lcg.LCGDataFormatError):
                lcg.load_numbers_from_file(bad)


class TestPrimality(unittest.TestCase):
    """Testy poprawności modułu testów pierwszości (Grupa 3)."""

    def test_mod_pow_binary_matches_builtin_pow(self) -> None:
        # Przykład ze slajdu 13/14: 5^100 mod 22 = 1
        self.assertEqual(primality.mod_pow_binary(5, 100, 22), 1)
        rng = random.Random(42)
        cases = [
            (0, 0, 7),
            (0, 5, 7),
            (7, 0, 1),
            (2, 10, 1024),
            (123456789, 65537, 999999937),
            (3, 560, 561),
        ]
        for _ in range(50):
            cases.append((rng.randint(0, 10**6), rng.randint(0, 10**6), rng.randint(1, 10**7)))
        for base, exp, mod in cases:
            self.assertEqual(
                primality.mod_pow_binary(base, exp, mod),
                pow(base, exp, mod),
                msg=f"Niezgodność dla ({base}^{exp}) mod {mod}",
            )

    def test_edge_cases_small_even_primes_and_composites(self) -> None:
        expected = {
            -7: False,
            0: False,
            1: False,
            2: True,
            3: True,
            4: False,
            5: True,
            6: False,
            7: True,
            9: False,
            11: True,
            15: False,
            25: False,
            97: True,
            100: False,
            7919: True,
            7921: False,  # 89^2
            104729: True,
            999999937: True,
        }
        rng_f = random.Random(100)
        rng_m = random.Random(100)
        for n, is_p in expected.items():
            self.assertEqual(primality.trial_division_by_primes(n), is_p, msg=f"trial({n})")
            self.assertEqual(primality.is_prime_exact_independent(n), is_p, msg=f"exact({n})")
            self.assertEqual(
                primality.miller_rabin_test(n, iterations=12, rng=rng_m),
                is_p,
                msg=f"MR({n})",
            )
            if is_p:
                # Fermat nigdy nie może odrzucić liczby pierwszej
                self.assertTrue(primality.fermat_test(n, iterations=12, rng=rng_f))
            else:
                self.assertFalse(primality.fermat_test(n, iterations=12, rng=rng_f))

    def test_carmichael_numbers_deceive_fermat_but_not_miller_rabin(self) -> None:
        # Liczby Carmichaela: dla każdej podstawy a względnie pierwszej z n zachodzi a^(n-1) = 1 (mod n)
        carmichaels = [561, 1105, 1729, 2465, 2821, 6601, 8911, 41041]
        fermat_fp_found = 0
        rng_f = random.Random(2026)
        rng_m = random.Random(2026)
        for c in carmichaels:
            self.assertFalse(primality.trial_division_by_primes(c))
            self.assertFalse(primality.is_prime_exact_independent(c))
            # Dla odpowiednio dużej liczby iteracji Miller–Rabin powinien wykryć złożoność
            self.assertFalse(primality.miller_rabin_test(c, iterations=20, rng=rng_m))
            # Przy 1-2 iteracjach test Fermata na wielu liczbach Carmichaela daje fałszywy wynik True
            if primality.fermat_test(c, iterations=2, rng=rng_f):
                fermat_fp_found += 1
        self.assertGreater(
            fermat_fp_found,
            0,
            msg="Oczekiwano, że przynajmniej jedna liczba Carmichaela zmyli test Fermata przy s=2.",
        )

    def test_benchmark_statistics_consistency(self) -> None:
        sample = [2, 3, 4, 17, 561, 1009, 1013, 1729, 2047, 7919]
        res = primality.benchmark_primality_methods(
            sample, iterations=5, rng_seed=12345, source_label="unit_test"
        )
        self.assertEqual(res["count"], len(sample))
        self.assertEqual(res["true_primes"], 6)
        self.assertEqual(res["true_composites"], 4)

        for method in ("trial_division_primes", "fermat", "miller_rabin"):
            summary = res["summaries"][method]
            raw_ns = [rec[f"{method}_ns"] for rec in res["records"]]
            self.assertEqual(summary["measurements"], len(sample))
            self.assertEqual(summary["min_ns"], min(raw_ns))
            self.assertEqual(summary["max_ns"], max(raw_ns))
            self.assertAlmostEqual(summary["mean_ns"], sum(raw_ns) / len(raw_ns), places=1)
            # Żaden z poprawnych testów nie może odrzucać liczb pierwszych
            self.assertEqual(summary["pseudocomposites_fn"], 0)
            if method == "trial_division_primes":
                self.assertEqual(summary["pseudoprimes_fp"], 0)


if __name__ == "__main__":
    unittest.main()
