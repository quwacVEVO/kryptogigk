import os
import re
import tempfile
import unittest

from kryptolib import preprocessing as p


class TestCzyszczenie(unittest.TestCase):
    def test_biale_znaki(self):
        self.assertEqual(p.usun_biale_znaki(" a\tb\nc  d "), "abcd")

    def test_diakrytyki(self):
        self.assertEqual(p.usun_znaki_diakrytyczne("Zażółć gęślą jaźń"), "Zazolc gesla jazn")
        self.assertEqual(p.usun_znaki_diakrytyczne("Łódź Źródło"), "Lodz Zrodlo")
        self.assertEqual(p.usun_znaki_diakrytyczne("øĐß Ærø"), "oDss AEro")
        self.assertEqual(p.usun_znaki_diakrytyczne("café naïve"), "cafe naive")

    def test_cyfry(self):
        self.assertEqual(p.usun_cyfry("a1b22c333"), "abc")

    def test_interpunkcja_i_symbole(self):
        self.assertEqual(p.usun_interpunkcje("a,b.c!d?e;f:g-h(i)[j]„k”«l»…—–→+=<>$%@#"), "abcdefghijkl")
        self.assertEqual(p.usun_interpunkcje("PG-4711 ok"), "PG4711 ok")

    def test_pelne_czyszczenie(self):
        self.assertEqual(p.pelne_czyszczenie("Zażółć, 123 gęślą!"), "Zazolcgesla")

    def test_wielkosc_liter(self):
        self.assertEqual(p.formatuj_wielkosc_liter("Ala"), "ALA")
        self.assertEqual(p.formatuj_wielkosc_liter("Ala", na_wielkie=False), "ala")


class TestKolumny(unittest.TestCase):
    def test_podzial(self):
        self.assertEqual(p.podziel_na_kolumny("A" * 12, kolumny=2, grupy=5), "AAAAA AAAAA\nAA")

    def test_bialy_znak_pominiety(self):
        self.assertEqual(p.podziel_na_kolumny("AB CD\nEF", kolumny=3, grupy=2), "AB CD EF")

    def test_domyslne_7x5(self):
        wiersze = p.podziel_na_kolumny("A" * 100).split("\n")
        self.assertEqual(wiersze[0], " ".join(["AAAAA"] * 7))
        self.assertEqual(len(wiersze), 3)


class TestTryby(unittest.TestCase):
    TEKST = "Zażółć gęślą jaźń! W 2026 roku, 4 października,\no godz. 22:30 -> Łódź;  ø ß."

    def test_alfa26(self):
        wynik = p.tryb_alfa26(self.TEKST)
        self.assertRegex(wynik, r"^[A-Z]+$")
        self.assertTrue(wynik.startswith("ZAZOLCGESLAJAZNWROKU"))
        self.assertTrue(wynik.endswith("LODZOSS"))

    def test_alfa37(self):
        wynik = p.tryb_alfa37(self.TEKST)
        self.assertRegex(wynik, r"^[A-Z0-9]+( [A-Z0-9]+)*$")   # pojedyncze spacje, bez brzegowych
        self.assertTrue(wynik.startswith("ZAZOLC GESLA JAZN W 2026"))
        self.assertIn("O GODZ 2230 LODZ O SS", wynik)           # brak podwójnej spacji po usuniętych znakach

    def test_alfa37_brzegi(self):
        self.assertEqual(p.tryb_alfa37("  Ala \n ma   kota  "), "ALA MA KOTA")
        self.assertEqual(p.tryb_alfa37("a - b"), "A B")

    def test_puste(self):
        self.assertEqual(p.tryb_alfa26("123 !?"), "")
        self.assertEqual(p.tryb_alfa37("!?"), "")

    def test_przygotuj_tekst(self):
        self.assertEqual(p.przygotuj_tekst("Ala ma 3 koty", "alfa26"), "ALAMAKOTY")
        self.assertEqual(p.przygotuj_tekst("Ala ma 3 koty", "ALFA37"), "ALA MA 3 KOTY")
        with self.assertRaises(ValueError):
            p.przygotuj_tekst("a", "ALFA99")


class TestPliki(unittest.TestCase):
    def test_zapis_i_odczyt(self):
        with tempfile.TemporaryDirectory() as d:
            sciezka = os.path.join(d, "t.txt")
            tekst = "Zażółć gęślą jaźń\nlinia 2"
            p.zapisz_do_pliku(sciezka, tekst)
            self.assertEqual(p.wczytaj_z_pliku(sciezka), tekst)

    def test_bom_z_notatnika(self):
        with tempfile.TemporaryDirectory() as d:
            sciezka = os.path.join(d, "bom.txt")
            with open(sciezka, "w", encoding="utf-8-sig") as f:
                f.write("Ala")
            self.assertEqual(p.wczytaj_z_pliku(sciezka), "Ala")


if __name__ == "__main__":
    unittest.main()
