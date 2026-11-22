import tempfile
import unittest
from pathlib import Path

from lab05.io_utils import read_integer_file, write_integer_file


class IntegerFileTests(unittest.TestCase):
    def test_round_trip(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "values.txt"
            write_integer_file(path, [1, -2, 300])
            self.assertEqual(read_integer_file(path), [1, -2, 300])

    def test_missing_file(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(FileNotFoundError):
                read_integer_file(Path(directory) / "missing.txt")

    def test_bad_format(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad.txt"
            path.write_text("1\nabc\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "linii 2"):
                read_integer_file(path)

    def test_empty_line_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad.txt"
            path.write_text("1\n\n2\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Pusty wiersz"):
                read_integer_file(path)


if __name__ == "__main__":
    unittest.main()
