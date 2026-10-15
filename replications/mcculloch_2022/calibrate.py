"""Run the predeclared history-matching and rejection-sampling experiments."""

import argparse
from concurrent.futures import ProcessPoolExecutor
import hashlib
import itertools
import json
import math
from pathlib import Path
import random
import statistics
import subprocess
import sys

from pydantic import BaseModel

from independent import PaperModel

STUDY = Path(__file__).resolve().parent


class Trial(BaseModel):
    seed: int
    metabolism: int
    vision: int
    initial_population: int
    final_population: int


def evaluate(task):
    seed, metabolism, vision = task
    model = PaperModel(seed, metabolism, vision)
    initial = len(model.agents)
    for _ in range(30):
        model.step()
    return Trial(seed=seed, metabolism=metabolism, vision=vision,
                 initial_population=initial, final_population=len(model.agents))


def particle(task):
    index, prior, tolerance, label = task
    rng = random.Random(f"mcculloch-2022-{label}-{index}")
    trials = []
    for attempt in range(100000):
        metabolism, vision = rng.choice(prior)
        seed = int.from_bytes(hashlib.sha256(f"{label}:{index}:{attempt}".encode()).digest(), "big")
        result = evaluate((seed, metabolism, vision))
        trials.append(result)
        if abs(result.final_population - 66) <= tolerance:
            return trials
    raise RuntimeError("No particle accepted within the declared attempt bound")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--particles", type=int, default=10000)
    args = parser.parse_args()
    assert args.workers > 0 and args.particles > 0
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    files = [Path(__file__), STUDY / "independent.py", STUDY / "CALIBRATION_PROTOCOL.md",
             STUDY / "published_calibration.json", STUDY / "requirements.lock", STUDY / "sugarscape_cg/sugar-map.txt"]
    provenance = {
        "command": sys.argv, "python": sys.version,
        "revision": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=STUDY, text=True).strip(),
        "working_tree": subprocess.check_output(["git", "status", "--porcelain"], cwd=STUDY, text=True),
        "sha256": {str(p.relative_to(STUDY)): hashlib.sha256(p.read_bytes()).hexdigest() for p in files},
    }
    (output / "provenance.json").write_text(json.dumps(provenance, indent=2) + "\n")
    prior = list(itertools.product(range(1, 5), range(1, 17)))
    waves = []
    seed = 1000000
    with ProcessPoolExecutor(args.workers) as pool, (output / "trials.jsonl").open("w") as log:
        for wave in range(1, 51):
            test_space = prior[::math.ceil(len(prior) / 4)]
            tasks = []
            for metabolism, vision in test_space:
                for _ in range(200):
                    tasks.append((seed, metabolism, vision))
                    seed += 1
            ensemble = list(pool.map(evaluate, tasks))
            for trial in ensemble:
                log.write(json.dumps({"phase": "ensemble", "wave": wave, **trial.model_dump()}) + "\n")
            variance = statistics.mean(statistics.variance(abs(t.final_population - 66) for t in ensemble
                                       if (t.metabolism, t.vision) == point) for point in test_space)
            uncertainty = 2 * variance
            tasks = [(seed + index, m, v) for index, (m, v) in enumerate(prior)]
            seed += len(tasks)
            predictions = list(pool.map(evaluate, tasks))
            for trial in predictions:
                log.write(json.dumps({"phase": "wave", "wave": wave, **trial.model_dump()}) + "\n")
            scores = [abs(t.final_population - 66) / math.sqrt(uncertainty) for t in predictions]
            retained = [point for point, score in zip(prior, scores) if score < 3]
            waves.append({"wave": wave, "prior": prior, "uncertainty": uncertainty,
                          "implausibility": scores, "retained": retained})
            (output / "waves.json").write_text(json.dumps(waves, indent=2) + "\n")
            log.flush()
            print(f"Wave {wave}: {len(prior)} -> {len(retained)}, variance {uncertainty:.6f}", flush=True)
            assert retained, "History matching eliminated the complete parameter space"
            converged = len(retained) == len(prior)
            prior = retained
            if converged:
                break
        assert converged, "History matching did not converge within 50 waves"
        published = json.loads((STUDY / "published_calibration.json").read_text())
        original = published["waves"][-1]
        experiments = (("pipeline", prior, uncertainty),
                       ("conditional", original["plaus_space"], original["uncert"]))
        for label, space, total_variance in experiments:
            tasks = [(index, space, math.sqrt(total_variance), label) for index in range(args.particles)]
            with (output / f"{label}-particles.jsonl").open("w") as particles:
                for index, trials in enumerate(pool.map(particle, tasks)):
                    for attempt, trial in enumerate(trials):
                        log.write(json.dumps({"phase": label, "particle": index, "attempt": attempt + 1,
                                              **trial.model_dump()}) + "\n")
                    particles.write(json.dumps({"particle": index, "attempts": len(trials),
                                                **trials[-1].model_dump()}) + "\n")
                    if (index + 1) % 500 == 0:
                        particles.flush()
                        log.flush()
                        print(f"{label}: {index + 1}/{args.particles} accepted", flush=True)
    (output / "complete.json").write_text(json.dumps({"waves": len(waves), "particles_per_experiment": args.particles}) + "\n")


if __name__ == "__main__":
    main()
