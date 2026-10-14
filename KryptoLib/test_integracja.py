"""Spójność całej biblioteki: preprocessing + szyfry + klucze."""
import unittest

from kryptolib import afiniczny as af
from kryptolib import klucze as k
from kryptolib import monoalfabetyczny as m
from kryptolib import preprocessing as p
from kryptolib.alfabety import ALFA26, ALFA37, get_alphabet

SUROWY = ("Zażółć gęślą jaźń! W 2026 roku, 4 października, o godz. 22:30 "
          "w Gdańsku padało 17 mm deszczu. Kod: PG-4711 (Łódź → Źródło).")
TRYBY = ("ALFA26", "ALFA37")


class TestPotok(unittest.TestCase):
    def test_preprocessing_daje_tekst_akceptowany_przez_szyfry(self):
        for tryb in TRYBY:
            t = p.przygotuj_tekst(SUROWY, tryb)
            self.assertEqual(m.decrypt(m.encrypt(t, k.caesar_key(5, tryb), tryb), k.caesar_key(5, tryb), tryb), t)
            self.assertEqual(af.deszyfruj_afiniczny(af.szyfruj_afiniczny(t, 7, 12, tryb), 7, 12, tryb), t)

    def test_surowy_tekst_jest_odrzucany(self):
        for tryb in TRYBY:
            with self.assertRaises(ValueError):
                m.encrypt(SUROWY, k.atbash_key(tryb), tryb)
            with self.assertRaises(ValueError):
                af.szyfruj_afiniczny(SUROWY, 5, 8, tryb)


class TestAfinicznyJakoMonoalfabetyczny(unittest.TestCase):
    def test_ten_sam_wynik(self):
        for tryb in TRYBY:
            t = p.przygotuj_tekst(SUROWY, tryb)
            m_ = len(get_alphabet(tryb))
            for a in af.poprawne_a(tryb)[:6]:
                for b in (0, 1, 8, m_ - 1):
                    klucz = k.affine_key(a, b, tryb)
                    self.assertEqual(m.encrypt(t, klucz, tryb), af.szyfruj_afiniczny(t, a, b, tryb))
                    c = af.szyfruj_afiniczny(t, a, b, tryb)
                    self.assertEqual(m.decrypt(c, klucz, tryb), t)

    def test_cezar_to_afiniczny_a1(self):
        for tryb in TRYBY:
            m_ = len(get_alphabet(tryb))
            for s in range(m_):
                self.assertEqual(k.caesar_key(s, tryb), k.affine_key(1, s, tryb))

    def test_atbash_to_afiniczny_minus1(self):
        for tryb in TRYBY:
            m_ = len(get_alphabet(tryb))
            self.assertEqual(k.atbash_key(tryb), k.affine_key(m_ - 1, m_ - 1, tryb))

    def test_liczba_roznych_kluczy_afinicznych(self):
        for tryb, oczekiwana in (("ALFA26", 12 * 26), ("ALFA37", 36 * 37)):
            m_ = len(get_alphabet(tryb))
            klucze = {k.affine_key(a, b, tryb) for a in af.poprawne_a(tryb) for b in range(m_)}
            self.assertEqual(len(klucze), oczekiwana)

    def test_affine_key_zle_a(self):
        with self.assertRaises(ValueError):
            k.affine_key(13, 0, "ALFA26")


class TestKluczeZgodnoscNazw(unittest.TestCase):
    def test_polskie_aliasy(self):
        self.assertEqual(k.klucz_cezara(3), k.caesar_key(3))
        self.assertEqual(k.klucz_atbasz(), k.atbash_key())
        self.assertEqual(k.klucz_rot13(), k.rot13_key())
        self.assertEqual(k.klucz_gaderypoluki("POLITYKARENU"), k.gaderypoluki_key("POLITYKARENU"))
        self.assertEqual(k.klucz_afiniczny(5, 8), k.affine_key(5, 8))

    def test_wszystkie_klucze_sa_permutacjami(self):
        for tryb in TRYBY:
            wszystkie = [k.caesar_key(s, tryb) for s in range(-40, 40)]
            wszystkie += [k.atbash_key(tryb), k.rot13_key(tryb)]
            wszystkie += [k.gaderypoluki_key(f, tryb) for f in k.GADERYPOLUKI_FRAZY.values()]
            for klucz in wszystkie:
                m.validate_key(klucz, tryb)

    def test_dlugosci_kluczy(self):
        self.assertEqual(len(k.klucz_cezara(1)), 26)
        self.assertEqual(len(k.caesar_key(1, "ALFA37")), 37)

    def test_co_najmniej_trzy_frazy_gaderypoluki(self):
        self.assertGreaterEqual(len(k.GADERYPOLUKI_FRAZY), 3)

    def test_alfabety_wspolne(self):
        self.assertIs(m.ALFA26, ALFA26)
        self.assertIs(m.ALFA37, ALFA37)


if __name__ == "__main__":
    unittest.main()
