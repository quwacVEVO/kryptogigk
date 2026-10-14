import math
import unittest

from kryptolib import afiniczny as af
from kryptolib.alfabety import get_alphabet


class TestMatematyka(unittest.TestCase):
    def test_nwd_rozszerzony(self):
        for a, b in ((240, 46), (17, 26), (5, 37), (0, 7), (13, 26)):
            g, x, y = af.nwd_rozszerzony(a, b)
            self.assertEqual(g, math.gcd(a, b))
            self.assertEqual(a * x + b * y, g)

    def test_odwrotnosc(self):
        for m in (26, 37):
            for a in range(1, m):
                if math.gcd(a, m) == 1:
                    self.assertEqual(a * af.odwrotnosc_modularna(a, m) % m, 1)
        self.assertEqual(af.odwrotnosc_modularna(-3, 26), af.odwrotnosc_modularna(23, 26))

    def test_brak_odwrotnosci(self):
        with self.assertRaises(ValueError):
            af.odwrotnosc_modularna(13, 26)

    def test_poprawne_a(self):
        self.assertEqual(af.poprawne_a("ALFA26"), [1, 3, 5, 7, 9, 11, 15, 17, 19, 21, 23, 25])
        self.assertEqual(af.poprawne_a("ALFA37"), list(range(1, 37)))


class TestSzyfr(unittest.TestCase):
    def test_znany_przyklad(self):
        self.assertEqual(af.szyfruj_afiniczny("AFFINECIPHER", 5, 8), "IHHWVCSWFRCP")
        self.assertEqual(af.deszyfruj_afiniczny("IHHWVCSWFRCP", 5, 8), "AFFINECIPHER")

    def test_roundtrip_wszystkie_klucze(self):
        teksty = {"ALFA26": "ZAZOLCGESLAJAZN", "ALFA37": "ZAZOLC GESLA 2026 JAZN"}
        for tryb, t in teksty.items():
            m = len(get_alphabet(tryb))
            for a in af.poprawne_a(tryb):
                for b in range(m):
                    self.assertEqual(af.deszyfruj_afiniczny(af.szyfruj_afiniczny(t, a, b, tryb), a, b, tryb), t)

    def test_b_spoza_zakresu_i_ujemne(self):
        t = "ALAMAKOTA"
        self.assertEqual(af.szyfruj_afiniczny(t, 5, 8 + 26), af.szyfruj_afiniczny(t, 5, 8))
        self.assertEqual(af.szyfruj_afiniczny(t, 5, -18), af.szyfruj_afiniczny(t, 5, 8))
        self.assertEqual(af.deszyfruj_afiniczny(af.szyfruj_afiniczny(t, -3, 4), -3, 4), t)

    def test_zle_a(self):
        for a, tryb in ((2, "ALFA26"), (13, "ALFA26"), (0, "ALFA26"), (26, "ALFA26"), (37, "ALFA37"), (0, "ALFA37")):
            with self.assertRaises(ValueError):
                af.szyfruj_afiniczny("A", a, 1, tryb)
            with self.assertRaises(ValueError):
                af.deszyfruj_afiniczny("A", a, 1, tryb)

    def test_restrykcyjnosc(self):
        with self.assertRaises(ValueError):
            af.szyfruj_afiniczny("Ala ma kota", 5, 8)            # małe litery i spacje w ALFA26
        with self.assertRaises(ValueError):
            af.deszyfruj_afiniczny("AB CD", 5, 8, "ALFA26")      # spacja nie jest po cichu pomijana
        with self.assertRaises(ValueError):
            af.szyfruj_afiniczny("A", 5, 8, "ALFA99")

    def test_pusty(self):
        self.assertEqual(af.szyfruj_afiniczny("", 5, 8), "")


if __name__ == "__main__":
    unittest.main()
