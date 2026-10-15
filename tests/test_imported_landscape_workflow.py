"""Exercise landscape import, simulation, and JSON telemetry through the CLI."""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


class ImportedLandscapeWorkflow(unittest.TestCase):
    def test_named_resources_rectangular_dimensions_and_initial_observation(self):
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory(prefix="sugarscape-landscape-") as temporary:
            directory = Path(temporary)
            for resource in ("sugar", "spice"):
                with self.subTest(resource=resource):
                    landscape = [[{"sugar": 0, "spice": 0} for _ in range(5)] for _ in range(7)]
                    for column in landscape:
                        for cell in column:
                            cell[resource] = 4
                    map_path = directory / f"{resource}-map.json"
                    map_path.write_text(json.dumps(landscape))
                    runs = []
                    for repeat in range(2):
                        log = directory / f"{resource}-{repeat}.json"
                        config = {
                            "seed": 17, "headlessMode": True, "startingAgents": 1,
                            "timesteps": 20, "logfile": str(log),
                            "environmentFile": str(map_path),
                            "agentVision": [1, 1], "agentMovement": [1, 1],
                            "agentStartingSugar": [0, 0], "agentStartingSpice": [0, 0],
                            "agentSugarMetabolism": [0, 0], "agentSpiceMetabolism": [0, 0],
                            "environmentSugarRegrowRate": 0, "environmentSpiceRegrowRate": 0,
                        }
                        config[f"agentStarting{resource.title()}"] = [10, 10]
                        config[f"agent{resource.title()}Metabolism"] = [1, 1]
                        config[f"environment{resource.title()}RegrowRate"] = 1
                        config_path = directory / "config.json"
                        config_path.write_text(json.dumps(config))
                        result = subprocess.run(
                            [sys.executable, str(root / "sugarscape.py"), "--conf", str(config_path)],
                            cwd=root, env={**os.environ, "PYTHONHASHSEED": "0"},
                            capture_output=True, text=True,
                        )
                        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                        observations = json.loads(log.read_text())
                        self.assertEqual([r["timestep"] for r in observations], list(range(21)))
                        self.assertEqual([r["population"] for r in observations], [1] * 21)
                        self.assertEqual(observations[0]["environmentWealthTotal"], 7 * 5 * 4)
                        self.assertEqual(observations[0]["agentWealthTotal"], 10)
                        self.assertGreater(observations[-1]["agentWealthTotal"], 10)
                        runs.append(observations)
                    self.assertEqual(runs[0], runs[1])


if __name__ == "__main__":
    unittest.main()
