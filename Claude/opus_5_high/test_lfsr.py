"""Testy poprawności generatora LFSR.

Odniesienie: notatka "Kryptologia lab05", slajd 6 (cztery przykłady: wektor p,
ziarno S i polecenie wygenerowania 32 bitów).
"""

import os
import unittest

import params
from common import read_numbers
from lfsr import (LFSR, bits_from_int, bits_needed, check_k_fits_interval, int_from_bits)


class TestPrzykladyZNotatki(unittest.TestCase):
    """p = (1,1,0), S = (0,0,1) itd. - przykłady wprost z notatki."""

    def test_pierwszy_przyklad_krok_po_kroku(self):
        # Przejście stanów policzone ręcznie z definicji S_{i+n} = suma p_j S_{i+j}:
        # (0,0,1) -> (0,1,0) -> (1,0,1) -> (0,1,1) -> (1,1,1) -> (1,1,0) -> (1,0,0) -> (0,0,1)
        generator = LFSR(3, [1, 1, 0], [0, 0, 1])
        oczekiwane_stany = [(0, 1, 0), (1, 0, 1), (0, 1, 1), (1, 1, 1), (1, 1, 0), (1, 0, 0), (0, 0, 1)]
        oczekiwane_bity = [0, 0, 1, 0, 1, 1, 1]
        for expected_state, expected_bit in zip(oczekiwane_stany, oczekiwane_bity):
            self.assertEqual(generator.next_bit(), expected_bit)
            self.assertEqual(generator.state_bits(), expected_state)

    def test_okresy_czterech_przykladow_z_notatki(self):
        # Okres jest tu MIERZONY; wartości teoretyczne: dla wielomianu pierwotnego 2^n - 1,
        # a dla x^4+x^3+x^2+x+1 (dzielnika x^5-1) okres 5.
        przyklady = [
            (3, [1, 1, 0], [0, 0, 1], 7),
            (4, [1, 1, 0, 0], [0, 0, 0, 1], 15),
            (4, [1, 1, 1, 1], [1, 0, 0, 1], 5),
            (6, [1, 1, 0, 1, 1, 0], [0, 0, 1, 0, 0, 1], 63),
        ]
        for n, taps, seed, expected_period in przyklady:
            with self.subTest(taps=taps):
                generator = LFSR(n, taps, seed)
                self.assertEqual(generator.period(), (0, expected_period))

    def test_32_bity_sa_okresowe_z_okresem_rejestru(self):
        generator = LFSR(3, [1, 1, 0], [0, 0, 1])
        bits = generator.bits(32)
        for index in range(32 - 7):
            self.assertEqual(bits[index], bits[index + 7])

    def test_bit_wyjsciowy_to_zawsze_pierwszy_bit_stanu(self):
        generator = LFSR(4, [1, 0, 0, 1], [1, 0, 1, 1])
        for _ in range(20):
            expected = generator.state_bits()[0]
            self.assertEqual(generator.next_bit(), expected)


class TestWalidacjaParametrow(unittest.TestCase):
    def test_zbyt_krotki_rejestr(self):
        with self.assertRaises(ValueError):
            LFSR(1, [1], [1])

    def test_dlugosc_niecalkowita(self):
        with self.assertRaises(ValueError):
            LFSR(4.0, [1, 1, 0, 0], [0, 0, 0, 1])

    def test_zla_dlugosc_wektora_odczepow(self):
        with self.assertRaises(ValueError):
            LFSR(4, [1, 1], [0, 0, 0, 1])

    def test_zla_dlugosc_ziarna(self):
        with self.assertRaises(ValueError):
            LFSR(4, [1, 1, 0, 0], [0, 1])

    def test_wartosci_inne_niz_bity(self):
        with self.assertRaises(ValueError):
            LFSR(3, [1, 2, 0], [0, 0, 1])
        with self.assertRaises(ValueError):
            LFSR(3, [1, 1, 0], [0, 0, "x"])

    def test_brak_sprzezenia(self):
        with self.assertRaises(ValueError):
            LFSR(4, [0, 0, 0, 0], [1, 0, 0, 1])

    def test_ziarno_zerowe_jest_blokowane_domyslnie(self):
        with self.assertRaises(ValueError) as caught:
            LFSR(4, [1, 1, 0, 0], [0, 0, 0, 0])
        self.assertIn("zerowe", str(caught.exception))

    def test_ziarno_zerowe_dopuszczone_jawnie_daje_ciag_zerowy(self):
        generator = LFSR(4, [1, 1, 0, 0], [0, 0, 0, 0], allow_zero_seed=True)
        self.assertEqual(generator.bits(16), [0] * 16)
        generator.reset()
        self.assertEqual(generator.period(), (0, 1))

    def test_indeks_odczepu_poza_zakresem(self):
        with self.assertRaises(ValueError):
            LFSR.from_tap_indices(4, [0, 9], 1)

    def test_ziarno_nie_miesci_sie_w_rejestrze(self):
        with self.assertRaises(ValueError):
            LFSR.from_tap_indices(4, [0, 1], 16)

    def test_ujemne_ziarno(self):
        with self.assertRaises(ValueError):
            LFSR.from_tap_indices(4, [0, 1], -1)


class TestKonwersjeBitow(unittest.TestCase):
    def test_bity_i_liczba_sa_odwracalne(self):
        for value in range(16):
            self.assertEqual(int_from_bits(bits_from_int(value, 4)), value)

    def test_pierwszy_bit_jest_najbardziej_znaczacy(self):
        self.assertEqual(bits_from_int(8, 4), [1, 0, 0, 0])

    def test_liczba_bitow_na_zakres(self):
        self.assertEqual(bits_needed(1), 0)
        self.assertEqual(bits_needed(2), 1)
        self.assertEqual(bits_needed(1000), 10)
        self.assertEqual(bits_needed(1024), 10)
        self.assertEqual(bits_needed(1025), 11)


class TestMapowanieNaPrzedzial(unittest.TestCase):
    def generator(self):
        return LFSR.from_tap_indices(params.LFSR_N, params.LFSR_TAP_INDICES, params.LFSR_SEED)

    def test_wszystkie_liczby_sa_w_przedziale(self):
        for low, high in [(1, 1000), (0, 1), (-50, 50), (7, 7), (10 ** 9, 10 ** 12)]:
            with self.subTest(low=low, high=high):
                numbers = self.generator().numbers(300, low, high)
                self.assertTrue(all(low <= value <= high for value in numbers))
                self.assertEqual(len(numbers), 300)

    def test_przedzial_jednoelementowy_daje_stala(self):
        self.assertEqual(self.generator().numbers(5, 7, 7), [7] * 5)

    def test_oba_konce_przedzialu_sa_osiagalne(self):
        numbers = self.generator().numbers(20000, 1, 10)
        self.assertEqual(min(numbers), 1)
        self.assertEqual(max(numbers), 10)

    def test_tryb_reject_daje_rozklad_bez_obciazenia_modulo(self):
        # Dla span = 3 i 2-bitowych słów tryb "mod" nadreprezentuje dolną część
        # przedziału, a tryb "reject" nie. Sprawdzamy na pełnym okresie.
        generator = self.generator()
        reject = generator.numbers(30000, 1, 3, mode="reject")
        generator.reset()
        modulo = generator.numbers(30000, 1, 3, mode="mod")
        reject_udzial = reject.count(1) / len(reject)
        modulo_udzial = modulo.count(1) / len(modulo)
        self.assertLess(abs(reject_udzial - 1 / 3), 0.02)
        self.assertGreater(modulo_udzial, 0.45)

    def test_pusty_przedzial(self):
        with self.assertRaises(ValueError):
            self.generator().numbers(5, 10, 1)

    def test_nieznany_tryb(self):
        with self.assertRaises(ValueError):
            self.generator().numbers(5, 1, 10, mode="losowy")

    def test_niecalkowite_konce_przedzialu(self):
        with self.assertRaises(ValueError):
            self.generator().numbers(5, 1.5, 10)


class TestCiagBezPowtorzen(unittest.TestCase):
    def test_warunek_K_mniejsze_rowne_span(self):
        ok, message = check_k_fits_interval(200, 1, 1000)
        self.assertTrue(ok)
        self.assertIn("jest możliwy", message)
        ok, message = check_k_fits_interval(1001, 1, 1000)
        self.assertFalse(ok)
        self.assertIn("NIEMOŻLIWY", message)

    def test_filtr_powtorzen_daje_rozne_liczby(self):
        generator = LFSR.from_tap_indices(params.LFSR_N, params.LFSR_TAP_INDICES, params.LFSR_SEED)
        numbers = generator.unique_numbers(200, 1, 1000)
        self.assertEqual(len(numbers), 200)
        self.assertEqual(len(set(numbers)), 200)
        self.assertTrue(all(1 <= value <= 1000 for value in numbers))

    def test_zbyt_duze_K_jest_odrzucane_przed_generowaniem(self):
        generator = LFSR.from_tap_indices(params.LFSR_N, params.LFSR_TAP_INDICES, params.LFSR_SEED)
        with self.assertRaises(ValueError) as caught:
            generator.unique_numbers(1001, 1, 1000)
        self.assertIn("K <= b - a + 1", str(caught.exception))

    def test_zbyt_krotki_okres_nie_pokryje_przedzialu(self):
        # Rejestr o okresie 15 nie wygeneruje 100 różnych liczb z [1, 1000].
        generator = LFSR(4, [1, 1, 0, 0], [0, 0, 0, 1])
        with self.assertRaises(RuntimeError):
            generator.unique_numbers(100, 1, 1000)


class TestOdtwarzalnoscWynikow(unittest.TestCase):
    """Zgodność zapisanych plików wynikowych z ponownym uruchomieniem generatora."""

    def test_plik_glowny_zgadza_sie_z_ponownym_wygenerowaniem(self):
        path = os.path.join(params.RESULTS_DIR, "lfsr_numbers_main.txt")
        if not os.path.exists(path):
            self.skipTest("brak {} - uruchom najpierw exp_lfsr.py".format(path))
        generator = LFSR.from_tap_indices(params.LFSR_N, params.LFSR_TAP_INDICES, params.LFSR_SEED)
        expected = generator.numbers(params.K, params.LOW, params.HIGH, mode=params.LFSR_MAPPING)
        self.assertEqual(read_numbers(path), expected)

    def test_ten_sam_stan_daje_ten_sam_ciag(self):
        first = LFSR.from_tap_indices(16, (0, 2, 3, 5), 0xACE1).numbers(50, 1, 1000)
        second = LFSR.from_tap_indices(16, (0, 2, 3, 5), 0xACE1).numbers(50, 1, 1000)
        self.assertEqual(first, second)

    def test_rozne_ziarna_daja_rozne_ciagi(self):
        first = LFSR.from_tap_indices(16, (0, 2, 3, 5), 1).numbers(50, 1, 1000)
        second = LFSR.from_tap_indices(16, (0, 2, 3, 5), 2).numbers(50, 1, 1000)
        self.assertNotEqual(first, second)


class TestOkresIBilansBitow(unittest.TestCase):
    def test_wielomian_pierwotny_daje_okres_maksymalny(self):
        generator = LFSR.from_tap_indices(16, (0, 2, 3, 5), 1)
        self.assertEqual(generator.period(max_steps=70000), (0, 2 ** 16 - 1))

    def test_odczepy_bez_p0_moga_dac_ogon(self):
        generator = LFSR.from_tap_indices(16, (5,), 0xACE1)
        tail, cycle = generator.period(max_steps=70000)
        self.assertGreater(tail, 0)
        self.assertGreater(cycle, 0)

    def test_bilans_jedynek_w_pelnym_okresie(self):
        generator = LFSR.from_tap_indices(16, (0, 2, 3, 5), 1)
        ratio = generator.ones_ratio(2 ** 16 - 1)
        # Ciąg m-sekwencji ma 2^(n-1) jedynek na 2^n - 1 bitów.
        self.assertAlmostEqual(ratio, 2 ** 15 / (2 ** 16 - 1), places=9)

    def test_opis_wielomianu(self):
        generator = LFSR.from_tap_indices(4, (0, 1), 1)
        self.assertEqual(generator.polynomial(), "x^4 + x + 1")


if __name__ == "__main__":
    unittest.main()
