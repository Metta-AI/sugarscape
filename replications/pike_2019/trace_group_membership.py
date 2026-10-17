"""Retain native group-composition records without changing model execution."""

import argparse
import hashlib
import json
from pathlib import Path
import runpy
import sys

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("engine", type=Path)
parser.add_argument("library", type=Path)
parser.add_argument("approach", choices=["explicit", "network"])
parser.add_argument("threshold", type=int, choices=[1, 5, 10])
parser.add_argument("policy", choices=["none", "movement"])
parser.add_argument("seed", type=int)
parser.add_argument("output", type=Path)
args = parser.parse_args()
native_run = runpy.run_path
captured = []


def retain_composition(path, *positional, **keywords):
    namespace = native_run(path, *positional, **keywords)
    if Path(path).name == "run.py":
        model = namespace["m"]
        captured.append(model.meta_type)
        assert sum(a.type == "resource" for a in model.ml.schedule.values()) == 2500
    return namespace


runpy.run_path = retain_composition
runner = Path(__file__).with_name("run_groups.py")
sys.argv = [
    str(runner),
    str(args.engine),
    str(args.library),
    args.approach,
    str(args.threshold),
    args.policy,
    str(args.seed),
    str(args.output),
]
runpy.run_path(str(runner), run_name="__main__")
assert len(captured) == 1
records = captured[0]
assert set(records) == set(range(1, 1001))
observed = json.loads((args.output / "run" / "observations.json").read_text())
for row in observed:
    groups, independent = records[row["step"]]
    assert row["nested_group_edges"] == 0
    assert len(groups) == row["retained_groups"]
    assert independent == row["native_reporter"] - 2500 - row["retained_groups"]
    assert 0 <= independent <= row["individual_agents"]
(args.output / "native-composition.json").write_text(json.dumps(records) + "\n")
(args.output / "composition-audit.json").write_text(
    json.dumps(
        {
            "validated_steps": 1000,
            "resource_agents": 2500,
            "final_independent_agents": records[1000][1],
            "observer_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "scope": "Native schedule composition equals retained reporter minus resources and groups at all1000steps. Trajectory parity must be verified separately.",
        },
        indent=2,
    )
    + "\n"
)
