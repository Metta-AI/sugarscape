"""Complete-world system checks against the frozen released implementation."""

import os
import unittest
from itertools import product

from independent import PaperModel
from run import SeededReference, SsAgent, STUDY


class CompleteWorldEquivalence(unittest.TestCase):
    def test_full_world_trajectories(self):
        previous_directory = os.getcwd()
        os.chdir(STUDY)
        try:
            cases = [(metabolism, vision, seed)
                     for metabolism, vision in ((1, 1), (2, 10), (4, 7), (4, 16))
                     for seed in (0, 1, 42, 219)]
            cases.extend((metabolism, vision, 1000000)
                         for metabolism, vision in product(range(1, 5), range(1, 17)))
            for metabolism, vision, seed in cases:
                with self.subTest(metabolism=metabolism, vision=vision, seed=seed):
                    reference = SeededReference(seed=seed, max_metabolism=metabolism, max_vision=vision)
                    independent = PaperModel(seed=seed, max_metabolism=metabolism, max_vision=vision)
                    for tick in range(101):
                        self.assertEqual(len(independent.agents), reference.schedule.get_breed_count(SsAgent))
                        self.assertEqual(independent.random.getstate(), reference.random.getstate())
                        for identity, citizen in independent.agents.items():
                            original = reference.schedule.agents_by_breed[SsAgent][identity]
                            self.assertEqual((citizen.x, citizen.y, citizen.sugar), (*original.pos, original.sugar))
                        for x in range(50):
                            for y in range(50):
                                occupants = reference.grid.get_cell_list_contents([(x, y)])
                                self.assertEqual(independent.occupancy[x * 50 + y], len(occupants) - 1)
                                self.assertEqual(independent.sugar[x * 50 + y], occupants[0].amount)
                        if tick < 100:
                            reference.step()
                            independent.step()
        finally:
            os.chdir(previous_directory)


if __name__ == "__main__":
    unittest.main()
