"""Run the conditional inherited-trait experiment after full fixed-model parity gates."""

import argparse
from concurrent.futures import ThreadPoolExecutor
import csv
import hashlib
import json
from pathlib import Path
import subprocess
import time

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("experiment", type=Path)
args = parser.parse_args()
root = args.experiment.resolve()
repo = Path(__file__).resolve().parent
protocol = {
    "scope": "Conditional Figure 4 reconstruction, not recovered author code or Table 1 steady-state replication.",
    "initial_population": 830,
    "cycles": 500,
    "record_every": 1,
    "seeds": list(range(100)),
    "workers": 2,
    "per_run_timeout_seconds": 60,
    "initialization": "Distinct uniformly sampled cells by rejection sampling; zero wealth and age; independently uniform infertility in 10,20,...100 and birth cost in 0,10,...90.",
    "inheritance": "Newborn inherits both exact parental traits; no mutation, no trait reassignment, zero newborn wealth and age.",
    "conventions": "All fixed-model movement, scheduling, reproduction equality and regrowth rules retained. One recorded generation is assumed to be one action cycle for this reconstruction only.",
    "remaining_uncertainty": "Author initialization, joint trait assignment, inheritance/mutation and generation meaning unresolved. No fitted seeds or paper agreement threshold.",
    "qualification": "Two 1000-cycle one-agent homogeneous native runs must match the unchanged fixed simulator byte-for-byte in aggregate and individual observations.",
}
(root / "protocol.json").write_text(json.dumps(protocol, indent=2) + "\n")
for name in ["simulate.cpp", "build_evolution.py", "run_evolution.py"]:
    (root / name).write_bytes((repo / name).read_bytes())
fixed = root / "model/fixed"
subprocess.run(
    [
        "clang++",
        "-std=c++17",
        "-O2",
        "-Wall",
        "-Wextra",
        "-Werror",
        str(root / "simulate.cpp"),
        "-o",
        str(fixed),
    ],
    check=True,
)
manifest = {
    "compiler": subprocess.check_output(["clang++", "--version"], text=True),
    "sha256": {
        str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in [
            root / "protocol.json",
            root / "simulate.cpp",
            root / "build_evolution.py",
            root / "run_evolution.py",
            root / "model/simulate_evolution.cpp",
            root / "model/evolution",
            fixed,
        ]
    },
}
(root / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
qualification = root / "qualification"
qualification.mkdir(exist_ok=False)
for scenario, infertility, cost in [("low", 85, 0), ("cost", 10, 40)]:
    for variant in ["fixed", "evolution"]:
        stem = qualification / (scenario + "-" + variant)
        cmd = [
            str(root / "model" / variant),
            "0",
            str(infertility),
            str(cost),
            "1000",
            "1",
            str(stem) + ".observations.csv",
        ]
        if variant == "evolution":
            cmd += ["1", "0", str(stem) + ".traits.csv"]
        with (
            Path(str(stem) + ".csv").open("x") as out,
            Path(str(stem) + ".stderr").open("x") as err,
        ):
            subprocess.run(cmd, stdout=out, stderr=err, check=True, timeout=60)
    for suffix in [".csv", ".observations.csv"]:
        assert (qualification / (scenario + "-fixed" + suffix)).read_bytes() == (
            qualification / (scenario + "-evolution" + suffix)
        ).read_bytes()
(root / "qualification.json").write_text(
    json.dumps(
        {
            "complete_native_pairs": 2,
            "cycles_per_pair": 1000,
            "byte_exact_aggregate_files": 2,
            "byte_exact_observation_files": 2,
        },
        indent=2,
    )
    + "\n"
)
(root / "runs").mkdir(exist_ok=False)


def execute(seed):
    """Execute and audit one complete evolutionary workflow and its inheritance ledger."""
    target = root / "runs" / str(seed)
    target.mkdir(exist_ok=False)
    command = [
        str(root / "model/evolution"),
        str(seed),
        "10",
        "10",
        "500",
        "1",
        str(target / "observations.csv"),
        "830",
        "1",
        str(target / "traits.csv"),
    ]
    started = time.monotonic()
    with (
        (target / "aggregate.csv").open("x") as out,
        (target / "stderr").open("x") as err,
    ):
        result = subprocess.run(command, stdout=out, stderr=err, timeout=60)
    (target / "exit.json").write_text(
        json.dumps(
            {
                "exit_code": result.returncode,
                "command": command,
                "elapsed_seconds": time.monotonic() - started,
            },
            indent=2,
        )
        + "\n"
    )
    assert result.returncode == 0
    with (target / "aggregate.csv").open() as stream:
        rows = list(csv.DictReader(stream))
    assert [int(r["cycle"]) for r in rows] == list(range(1, int(rows[-1]["cycle"]) + 1))
    assert int(rows[-1]["cycle"]) == 500 or int(rows[-1]["population"]) == 0
    assert all(int(r["conservation_error"]) == 0 for r in rows)
    traits = {}
    joint = {}
    births = {}
    birth_costs = {}
    inherited = 0
    with (target / "traits.csv").open() as stream:
        for r in csv.DictReader(stream):
            cycle = int(r["cycle"])
            identity = int(r["id"])
            pair = (int(r["infertility"]), int(r["birth_cost"]))
            count = int(r["count"])
            assert pair[0] in range(10, 101, 10) and pair[1] in range(0, 91, 10)
            if r["kind"] == "initial":
                assert cycle == 0 and identity not in traits and count == 1
                traits[identity] = pair
            elif r["kind"] == "birth":
                assert cycle > 0 and identity not in traits and count == 1
                assert traits[int(r["parent_id"])] == pair
                traits[identity] = pair
                inherited += 1
                births[cycle] = births.get(cycle, 0) + 1
                birth_costs[cycle] = birth_costs.get(cycle, 0) + pair[1]
            else:
                assert r["kind"] == "joint" and identity == -1 and count > 0
                key = (cycle, *pair)
                assert key not in joint
                joint[key] = count
    assert sum(count for (cycle, _, _), count in joint.items() if cycle == 0) == 830
    assert set(range(830)).issubset(traits)
    for r in rows:
        cycle = int(r["cycle"])
        assert sum(count for (t, _, _), count in joint.items() if t == cycle) == int(
            r["population"]
        )
        assert births.get(cycle, 0) == int(r["births"]) and birth_costs.get(
            cycle, 0
        ) == int(r["birth_loss"])
    record = {
        "seed": seed,
        "cycles": len(rows),
        "inheritance_events": inherited,
        "terminal_population": int(rows[-1]["population"]),
        "terminal_wealth": int(rows[-1]["wealth"]),
        "terminal_gini": float(rows[-1]["gini"]),
        "sha256": {
            p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in target.iterdir()
        },
    }
    (target / "audit.json").write_text(json.dumps(record, indent=2) + "\n")
    return record


with (
    (root / "completed.jsonl").open("x") as ledger,
    ThreadPoolExecutor(max_workers=2) as pool,
):
    for record in pool.map(execute, protocol["seeds"]):
        ledger.write(json.dumps(record) + "\n")
        ledger.flush()
(root / "complete.json").write_text(
    json.dumps({"complete_runs": 100, "scope": protocol["scope"]}, indent=2) + "\n"
)
print("100 conditional evolutionary runs completed and audited.", flush=True)
