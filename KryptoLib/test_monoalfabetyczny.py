import random
import unittest

from kryptolib import monoalfabetyczny as m
from kryptolib.alfabety import ALFA26, ALFA37, get_alphabet

TEKST26 = "THEQUICKBROWNFOXJUMPSOVERTHELAZYDOG"
TEKST37 = "ALA MA KOTA 123 I PSA 9"
TEKSTY = {"ALFA26": TEKST26, "ALFA37": TEKST37}


class TestSzyfrOgolny(unittest.TestCase):
    def test_znane_wyniki(self):
        self.assertEqual(m.caesar_encrypt("ABC", 3), "DEF")
        self.assertEqual(m.caesar_encrypt("XYZ", 3), "ABC")
        self.assertEqual(m.atbash_encrypt("ABCZ"), "ZYXA")
        self.assertEqual(m.rot13_encrypt("HELLO"), "URYYB")
        self.assertEqual(m.gaderypoluki_encrypt("ALAMAKOTA"), "GUGMGIPTG")

    def test_roundtrip_losowe_klucze(self):
        rng = random.Random(0)
        for mode, tekst in TEKSTY.items():
            alfa = list(get_alphabet(mode))
            for _ in range(50):
                rng.shuffle(alfa)
                key = "".join(alfa)
                self.assertEqual(m.decrypt(m.encrypt(tekst, key, mode), key, mode), tekst)
                self.assertEqual(m.invert_key(m.invert_key(key, mode), mode), key)

    def test_pusty_tekst(self):
        self.assertEqual(m.encrypt("", ALFA26), "")


class TestSzyfrySzczegolne(unittest.TestCase):
    def test_roundtrip(self):
        for mode, t in TEKSTY.items():
            for s in range(-40, 40):
                self.assertEqual(m.caesar_decrypt(m.caesar_encrypt(t, s, mode), s, mode), t)
            self.assertEqual(m.atbash_decrypt(m.atbash_encrypt(t, mode), mode), t)
            self.assertEqual(m.rot13_decrypt(m.rot13_encrypt(t, mode), mode), t)
            for fraza in m.GADERYPOLUKI_FRAZY.values():
                c = m.gaderypoluki_encrypt(t, fraza, mode)
                self.assertEqual(m.gaderypoluki_decrypt(c, fraza, mode), t)

    def test_inwolucje(self):
        for mode in TEKSTY:
            for k in (m.atbash_key(mode), m.rot13_key(mode), m.gaderypoluki_key("POLITYKARENU", mode)):
                self.assertEqual(m.invert_key(k, mode), k)

    def test_cezar_identycznosc(self):
        self.assertEqual(m.caesar_key(0), ALFA26)
        self.assertEqual(m.caesar_key(26), ALFA26)
        self.assertEqual(m.caesar_key(37, "ALFA37"), ALFA37)

    def test_rot13_alfa37(self):
        self.assertEqual(m.rot13_encrypt("A 1", "ALFA37"), "N 1")

    def test_gaderypoluki_myslniki(self):
        self.assertEqual(m.gaderypoluki_key("GA-DE-RY-PO-LU-KI"), m.gaderypoluki_key("GADERYPOLUKI"))

    def test_gaderypoluki_bledne_frazy(self):
        for fraza in ("ABC", "ABAC", "A1"):
            with self.assertRaises(ValueError):
                m.gaderypoluki_key(fraza)


class TestBledy(unittest.TestCase):
    def test_bledne_klucze(self):
        for key, mode in (("ABC", "ALFA26"), ("A" * 26, "ALFA26"),
                          (ALFA26[:-1] + "1", "ALFA26"), (ALFA26, "ALFA37")):
            with self.assertRaises(ValueError):
                m.encrypt("A", key, mode)

    def test_znak_spoza_alfabetu(self):
        with self.assertRaises(ValueError):
            m.encrypt("ala", m.atbash_key())
        with self.assertRaises(ValueError):
            m.encrypt("A 1", m.atbash_key("ALFA26"), "ALFA26")
        with self.assertRaises(ValueError):
            m.decrypt("abc", m.atbash_key())

    def test_nieznany_tryb(self):
        with self.assertRaises(ValueError):
            get_alphabet("ALFA99")


if __name__ == "__main__":
    unittest.main()
