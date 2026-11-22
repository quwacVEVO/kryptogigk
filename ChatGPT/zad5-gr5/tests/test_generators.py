import unittest

from lab05.generators import (
    LCG,
    LFSR,
    collision_stats,
    has_full_lcg_period,
    lcg_cycle_info,
    lfsr_cycle_info,
)


class LFSRTests(unittest.TestCase):
    def test_known_sequence_from_theory_convention(self):
        generator = LFSR(3, (0, 1), (0, 0, 1))
        self.assertEqual([generator.step() for _ in range(14)], [0, 0, 1, 0, 1, 1, 1] * 2)

    def test_known_cycle(self):
        self.assertEqual(lfsr_cycle_info(3, (0, 1), (0, 0, 1)).period, 7)

    def test_zero_seed_is_fixed_point(self):
        info = lfsr_cycle_info(8, (0, 2, 3, 4), (0,) * 8)
        self.assertEqual((info.preperiod, info.period), (0, 1))

    def test_values_stay_in_interval(self):
        values = LFSR(8, (0, 2, 3, 4), (0, 0, 0, 0, 0, 0, 0, 1)).generate(
            500, -20, 37
        )
        self.assertTrue(all(-20 <= value <= 37 for value in values))

    def test_invalid_parameters(self):
        with self.assertRaises(ValueError):
            LFSR(0, (0,), ())
        with self.assertRaises(ValueError):
            LFSR(3, (), (0, 0, 1))
        with self.assertRaises(ValueError):
            LFSR(3, (3,), (0, 0, 1))
        with self.assertRaises(ValueError):
            LFSR(3, (0, 0), (0, 0, 1))
        with self.assertRaises(ValueError):
            LFSR(3, (0, 1), (0, 2, 1))

    def test_impossible_rejection_mapping_does_not_hang(self):
        with self.assertRaises(RuntimeError):
            LFSR(1, (0,), (1,)).draw_int(0, 2)

    def test_checked_collision_free_example(self):
        values = LFSR(
            16,
            (0, 2, 3, 5),
            (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1),
        ).generate(200, 10_000, 59_999)
        self.assertEqual(len(values), len(set(values)))


class LCGTests(unittest.TestCase):
    def test_states_follow_equation(self):
        generator = LCG(16, 5, 1, 3)
        expected = [0, 1, 6, 15, 12, 13]
        self.assertEqual([generator.step() for _ in expected], expected)

    def test_example_from_theory_first_values(self):
        generator = LCG(134456, 8121, 28411, 55)
        self.assertEqual(
            [generator.step() for _ in range(5)],
            [71698, 93389, 108640, 128035, 52398],
        )

    def test_full_period_and_hull_dobell(self):
        self.assertTrue(has_full_lcg_period(256, 5, 1))
        info = lcg_cycle_info(256, 5, 1, 7)
        self.assertEqual((info.preperiod, info.period), (0, 256))

    def test_values_stay_in_interval(self):
        values = LCG(1024, 5, 1, 17).generate(500, 100, 999)
        self.assertTrue(all(100 <= value <= 999 for value in values))

    def test_interval_larger_than_modulus_is_rejected(self):
        with self.assertRaises(ValueError):
            LCG(16, 5, 1, 3).draw_int(0, 16)

    def test_invalid_parameters(self):
        with self.assertRaises(ValueError):
            LCG(1, 0, 0, 0)
        with self.assertRaises(ValueError):
            LCG(16, 16, 1, 0)
        with self.assertRaises(ValueError):
            LCG(16, 5, 16, 0)
        with self.assertRaises(ValueError):
            LCG(16, 5, 1, 16)

    def test_impossible_rejection_mapping_does_not_hang(self):
        with self.assertRaises(RuntimeError):
            LCG(16, 0, 15, 15).draw_int(0, 9)

    def test_checked_collision_free_example(self):
        values = LCG(65_536, 5, 1, 20_226).generate(200, 10_000, 59_999)
        self.assertEqual(len(values), len(set(values)))


class CollisionTests(unittest.TestCase):
    def test_collision_definitions(self):
        stats = collision_stats([4, 4, 4, 8, 9, 9])
        self.assertEqual(stats.unique_count, 3)
        self.assertEqual(stats.duplicate_occurrences, 3)
        self.assertEqual(stats.repeated_values, 2)
        self.assertEqual(stats.colliding_pairs, 4)


if __name__ == "__main__":
    unittest.main()
