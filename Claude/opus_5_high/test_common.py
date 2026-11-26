"""Testy narzędzi wspólnych: odczyt/zapis plików, kolizje, wykrywanie cyklu."""

import os
import tempfile
import unittest

from common import (BadNumberFile, collision_report, find_cycle, markdown_table,
                    minimal_period_of_block, read_numbers, sequence_period, time_stats,
                    write_numbers)


class TestPlikiZLiczbami(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.mkdtemp()

    def path(self, name):
        return os.path.join(self.folder, name)

    def test_zapis_i_odczyt_sa_odwracalne(self):
        numbers = [1, 2, 3, 1000, -5]
        path = write_numbers(self.path("a.txt"), numbers, header=["parametry testowe"])
        self.assertEqual(read_numbers(path), numbers)

    def test_komentarze_i_puste_wiersze_sa_pomijane(self):
        path = self.path("b.txt")
        with open(path, "w", encoding="utf-8") as handle:
            handle.write("# naglowek\n\n7\n   \n11\n")
        self.assertEqual(read_numbers(path), [7, 11])

    def test_brak_pliku_daje_zrozumialy_komunikat(self):
        with self.assertRaises(FileNotFoundError) as caught:
            read_numbers(self.path("nie_ma_takiego.txt"))
        self.assertIn("Brak pliku z danymi", str(caught.exception))

    def test_katalog_zamiast_pliku(self):
        with self.assertRaises(BadNumberFile):
            read_numbers(self.folder)

    def test_bledny_format_wskazuje_numer_wiersza(self):
        path = self.path("c.txt")
        with open(path, "w", encoding="utf-8") as handle:
            handle.write("5\n7\nnie_liczba\n")
        with self.assertRaises(BadNumberFile) as caught:
            read_numbers(path)
        self.assertIn(":3:", str(caught.exception))

    def test_liczba_zmiennoprzecinkowa_jest_bledem_formatu(self):
        path = self.path("d.txt")
        with open(path, "w", encoding="utf-8") as handle:
            handle.write("3.14\n")
        with self.assertRaises(BadNumberFile):
            read_numbers(path)

    def test_plik_bez_liczb(self):
        path = self.path("e.txt")
        with open(path, "w", encoding="utf-8") as handle:
            handle.write("# tylko komentarz\n")
        with self.assertRaises(BadNumberFile):
            read_numbers(path)


class TestKolizje(unittest.TestCase):
    def test_brak_kolizji(self):
        report = collision_report([1, 2, 3, 4])
        self.assertEqual(report["collisions"], 0)
        self.assertEqual(report["unique"], 4)
        self.assertIsNone(report["first_collision"])

    def test_wartosc_powtorzona_k_razy_wnosi_k_minus_jedna_kolizje(self):
        report = collision_report([5, 5, 5])
        self.assertEqual(report["collisions"], 2)
        self.assertEqual(report["max_multiplicity"], 3)
        self.assertEqual(report["first_collision"], (1, 5))

    def test_liczba_kolizji_to_dlugosc_minus_liczba_roznych(self):
        values = [1, 2, 2, 3, 3, 3, 9]
        report = collision_report(values)
        self.assertEqual(report["collisions"], len(values) - len(set(values)))


class TestCykle(unittest.TestCase):
    def test_czysty_cykl_bez_ogona(self):
        self.assertEqual(find_cycle(0, lambda s: (s + 1) % 7), (0, 7))

    def test_cykl_z_ogonem(self):
        # 0 -> 1 -> 2 -> 3 -> 1 (ogon 1, cykl 3)
        step = {0: 1, 1: 2, 2: 3, 3: 1}
        self.assertEqual(find_cycle(0, step.get), (1, 3))

    def test_punkt_staly(self):
        self.assertEqual(find_cycle(4, lambda s: 4), (0, 1))

    def test_brak_wykrycia_przy_limicie_krokow(self):
        self.assertEqual(find_cycle(0, lambda s: s + 1, max_steps=10), (None, None))

    def test_minimalny_okres_bloku(self):
        self.assertEqual(minimal_period_of_block([1, 2, 1, 2]), 2)
        self.assertEqual(minimal_period_of_block([1, 2, 3]), 3)
        self.assertEqual(minimal_period_of_block([4, 4, 4, 4]), 1)

    def test_okres_ciagu(self):
        self.assertEqual(sequence_period([1, 2, 3, 1, 2, 3]), 3)
        self.assertIsNone(sequence_period([1, 2, 3, 4]))


class TestStatystyki(unittest.TestCase):
    def test_statystyki_czasu(self):
        stats = time_stats([5, 1, 3])
        self.assertEqual((stats["n"], stats["min_ns"], stats["max_ns"]), (3, 1, 5))
        self.assertEqual(stats["mean_ns"], 3)
        self.assertEqual(stats["median_ns"], 3)

    def test_pusta_lista_czasow(self):
        self.assertEqual(time_stats([])["n"], 0)

    def test_tabela_markdown_ma_naglowek_i_separator(self):
        table = markdown_table(["a", "b"], [[1, 2]])
        self.assertEqual(table.splitlines()[0], "| a | b |")
        self.assertEqual(table.splitlines()[1], "|---|---|")


if __name__ == "__main__":
    unittest.main()
