"""Testy poprawności generatora LCG.

Odniesienie: notatka "Kryptologia lab05", slajdy 2-5 (wzór, pseudokod, tabela parametrów).
"""

import os
import unittest

import params
from common import read_numbers
from lcg import LCG, gcd, hull_dobell, prime_factors


class TestZgodnoscZRownaniem(unittest.TestCase):
    def test_kolejne_stany_spelniaja_wzor(self):
        generator = LCG(m=134456, a=8121, c=28411, x0=55)
        previous = 55
        for _ in range(100):
            current = generator.next_value()
            self.assertEqual(current, (8121 * previous + 28411) % 134456)
            previous = current

    def test_pierwszy_stan_zgodny_z_recznym_rachunkiem(self):
        # (8121 * 55 + 28411) mod 134456 = 474066 mod 134456 = 71698
        self.assertEqual(LCG(m=134456, a=8121, c=28411, x0=55).next_value(), 71698)

    def test_przyklad_z_tabeli_notatki(self):
        # a = 51, b (przyrost) = 13, m = 15; x0 = 1: (51*1+13) mod 15 = 64 mod 15 = 4
        generator = LCG(m=15, a=51, c=13, x0=1)
        self.assertEqual(generator.states(5), [4, 7, 10, 13, 1])

    def test_wszystkie_stany_sa_w_zakresie_modulu(self):
        generator = LCG(m=1000, a=21, c=3, x0=7)
        self.assertTrue(all(0 <= value < 1000 for value in generator.states(2000)))

    def test_funkcja_przejscia_jest_czysta(self):
        generator = LCG(m=100, a=7, c=3, x0=5)
        self.assertEqual(generator.next_state(5), 38)
        self.assertEqual(generator.state, 5)  # stan obiektu niezmieniony


class TestWalidacjaParametrow(unittest.TestCase):
    def test_zbyt_maly_modul(self):
        with self.assertRaises(ValueError):
            LCG(m=1, a=5, c=1, x0=0)

    def test_parametry_niecalkowite(self):
        with self.assertRaises(ValueError):
            LCG(m=100.0, a=5, c=1, x0=0)
        with self.assertRaises(ValueError):
            LCG(m=100, a="5", c=1, x0=0)

    def test_ujemne_a_lub_c(self):
        with self.assertRaises(ValueError):
            LCG(m=100, a=-5, c=1, x0=0)
        with self.assertRaises(ValueError):
            LCG(m=100, a=5, c=-1, x0=0)

    def test_ziarno_poza_zakresem(self):
        with self.assertRaises(ValueError):
            LCG(m=100, a=5, c=1, x0=100)
        with self.assertRaises(ValueError):
            LCG(m=100, a=5, c=1, x0=-1)

    def test_bool_nie_jest_poprawna_liczba(self):
        with self.assertRaises(ValueError):
            LCG(m=100, a=True, c=1, x0=0)


class TestOkresy(unittest.TestCase):
    def test_warunki_hull_dobella_i_zmierzony_okres_zgadzaja_sie(self):
        for m, a, c in [(65536, 25173, 13849), (1024, 5, 1), (1000, 21, 3)]:
            with self.subTest(m=m, a=a, c=c):
                ok, _ = hull_dobell(m, a, c)
                self.assertTrue(ok)
                tail, period = LCG(m=m, a=a, c=c, x0=1).period(max_steps=2 * m)
                self.assertEqual((tail, period), (0, m))

    def test_niespelnione_warunki_daja_krotszy_okres(self):
        ok, _ = hull_dobell(15, 51, 13)
        self.assertFalse(ok)
        self.assertEqual(LCG(m=15, a=51, c=13, x0=1).period(), (0, 5))

    def test_a_zero_daje_stala_i_ogon(self):
        tail, period = LCG(m=1000, a=0, c=37, x0=5).period()
        self.assertEqual((tail, period), (1, 1))

    def test_generator_multiplikatywny_ma_krotszy_okres_niz_m(self):
        tail, period = LCG(m=65536, a=25173, c=0, x0=2026).period()
        self.assertLess(period, 65536)

    def test_okres_nieustalony_przy_limicie(self):
        tail, period = LCG(m=2 ** 48, a=25214903917, c=11, x0=1).period(max_steps=1000)
        self.assertIsNone(period)
        self.assertIsNone(tail)

    def test_niezaleznosc_okresu_od_ziarna_przy_pelnym_okresie(self):
        for x0 in (0, 1, 2026, 65535):
            with self.subTest(x0=x0):
                self.assertEqual(LCG(m=65536, a=25173, c=13849, x0=x0).period(), (0, 65536))


class TestWarunkiHullDobella(unittest.TestCase):
    def test_nwd_wlasna_implementacja(self):
        self.assertEqual(gcd(12, 18), 6)
        self.assertEqual(gcd(13849, 65536), 1)
        self.assertEqual(gcd(0, 5), 5)

    def test_dzielniki_pierwsze(self):
        self.assertEqual(prime_factors(65536), {2})
        self.assertEqual(prime_factors(1000), {2, 5})
        self.assertEqual(prime_factors(13), {13})
        self.assertEqual(prime_factors(1), set())

    def test_c_zero_nie_spelnia_warunkow(self):
        ok, _ = hull_dobell(65536, 25173, 0)
        self.assertFalse(ok)


class TestMapowanieNaPrzedzial(unittest.TestCase):
    def generator(self):
        return LCG(m=params.LCG_M, a=params.LCG_A, c=params.LCG_C, x0=params.LCG_X0)

    def test_wszystkie_liczby_sa_w_przedziale(self):
        for mode in ("mod_reject", "mod", "scale"):
            for low, high in [(1, 1000), (0, 1), (-50, 50), (7, 7)]:
                with self.subTest(mode=mode, low=low, high=high):
                    numbers = self.generator().numbers(500, low, high, mode=mode)
                    self.assertEqual(len(numbers), 500)
                    self.assertTrue(all(low <= value <= high for value in numbers))

    def test_tryb_scale_dziala_gdy_m_mniejsze_od_span(self):
        generator = LCG(m=15, a=51, c=13, x0=1)
        numbers = generator.numbers(10, 1, 1000, mode="scale")
        self.assertTrue(all(1 <= value <= 1000 for value in numbers))

    def test_tryb_mod_reject_odrzuca_gdy_m_mniejsze_od_span(self):
        generator = LCG(m=15, a=51, c=13, x0=1)
        with self.assertRaises(ValueError) as caught:
            generator.numbers(10, 1, 1000, mode="mod_reject")
        self.assertIn("mod_reject", str(caught.exception))

    def test_mapowanie_bijektywne_daje_zero_kolizji_na_pelnym_okresie(self):
        generator = LCG(m=1024, a=5, c=1, x0=7)
        numbers = generator.numbers(1024, 1, 1024, mode="mod")
        self.assertEqual(len(set(numbers)), 1024)

    def test_pusty_przedzial_i_nieznany_tryb(self):
        with self.assertRaises(ValueError):
            self.generator().numbers(5, 10, 1)
        with self.assertRaises(ValueError):
            self.generator().numbers(5, 1, 10, mode="xyz")


class TestCiagBezPowtorzen(unittest.TestCase):
    def test_filtr_daje_rozne_liczby(self):
        numbers = LCG(m=params.LCG_M, a=params.LCG_A, c=params.LCG_C,
                      x0=params.LCG_X0).unique_numbers(200, 1, 1000)
        self.assertEqual(len(set(numbers)), 200)

    def test_zbyt_duze_K(self):
        generator = LCG(m=params.LCG_M, a=params.LCG_A, c=params.LCG_C, x0=params.LCG_X0)
        with self.assertRaises(ValueError) as caught:
            generator.unique_numbers(1001, 1, 1000)
        self.assertIn("K <= b - a + 1", str(caught.exception))

    def test_zbyt_krotki_okres_nie_pokryje_przedzialu(self):
        generator = LCG(m=15, a=51, c=13, x0=1)
        with self.assertRaises(RuntimeError):
            generator.unique_numbers(100, 1, 1000, mode="scale")


class TestOdtwarzalnoscWynikow(unittest.TestCase):
    def test_plik_glowny_zgadza_sie_z_ponownym_wygenerowaniem(self):
        path = os.path.join(params.RESULTS_DIR, "lcg_numbers_main.txt")
        if not os.path.exists(path):
            self.skipTest("brak {} - uruchom najpierw exp_lcg.py".format(path))
        generator = LCG(m=params.LCG_M, a=params.LCG_A, c=params.LCG_C, x0=params.LCG_X0)
        expected = generator.numbers(params.K, params.LOW, params.HIGH, mode=params.LCG_MAPPING)
        self.assertEqual(read_numbers(path), expected)

    def test_dwa_takie_same_generatory_daja_ten_sam_ciag(self):
        first = LCG(m=65536, a=25173, c=13849, x0=2026).numbers(100, 1, 1000)
        second = LCG(m=65536, a=25173, c=13849, x0=2026).numbers(100, 1, 1000)
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
