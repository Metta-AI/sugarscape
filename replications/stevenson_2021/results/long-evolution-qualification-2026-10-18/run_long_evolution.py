"""Run both conditional evolutionary scenarios to the declared long horizon."""

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
parser.add_argument("stable_reference", type=Path)
parser.add_argument("chaotic_reference", type=Path)
args = parser.parse_args()
root = args.experiment.resolve()
repo = Path(__file__).resolve().parent
root.mkdir(exist_ok=False)
protocol = {
    "scope": "Conditional inherited-trait long-run reconstruction; original initialization, inheritance and sampling conventions remain unresolved.",
    "cycles": 100000,
    "record_every": 100,
    "seeds": list(range(100)),
    "scenarios": {"stable": 10, "chaotic": 1},
    "initial_population": 830,
    "birth_cost_step": 10,
    "workers": 4,
    "per_run_timeout_seconds": 300,
    "global_seconds": 3600,
    "windows": [[35100, 50000], [75100, 100000]],
    "analysis": "Equal-weight seed means within each declared window for population, wealth, age and Gini; report seed SD and 95% confidence interval separately. Retain extinction and missing-window outcomes. No paper acceptance threshold or equilibrium claim.",
    "observation": "Aggregate, elite and founder observations every 100 cycles plus first/final/extinction; joint trait counts on the same schedule. Initial traits retained; birth-event export omitted after full native observer parity qualification.",
    "qualification": "Both scenarios, seed 0, 5000 cycles: dense and sparse engines must produce byte-identical aggregate/individual exports and identical joint observations at sampled cycles. Every ensemble run must match its retained 500-cycle prefix at all common sample times.",
}
(root / "protocol.json").write_text(json.dumps(protocol, indent=2) + "\n")
for name in [
    "simulate.cpp",
    "build_evolution.py",
    "build_long_evolution.py",
    "run_long_evolution.py",
]:
    (root / name).write_bytes((repo / name).read_bytes())
subprocess.run(
    ["python3", str(repo / "build_long_evolution.py"), str(root / "model")], check=True
)
for variant, source in [
    ("dense", "simulate_evolution.cpp"),
    ("sparse", "simulate_long_evolution.cpp"),
]:
    subprocess.run(
        [
            "clang++",
            "-std=c++17",
            "-O2",
            "-Wall",
            "-Wextra",
            "-Werror",
            str(root / "model" / source),
            "-o",
            str(root / "model" / variant),
        ],
        check=True,
    )
references = {
    "stable": args.stable_reference.resolve(),
    "chaotic": args.chaotic_reference.resolve(),
}
reference_records = {}
for scenario, reference in references.items():
    manifest = json.loads((reference / "manifest.json").read_text())
    for name, digest in manifest["sha256"].items():
        assert hashlib.sha256((reference / name).read_bytes()).hexdigest() == digest
    assert (reference / "model/simulate_evolution.cpp").read_bytes() == (
        root / "model/simulate_evolution.cpp"
    ).read_bytes()
    records = [
        json.loads(line)
        for line in (reference / "completed.jsonl").read_text().splitlines()
    ]
    assert [r["seed"] for r in records] == list(range(100))
    reference_records[scenario] = records
manifest = {
    "compiler": subprocess.check_output(["clang++", "--version"], text=True),
    "sha256": {
        str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in root.rglob("*")
        if p.is_file()
    },
    "references": {
        name: {
            "path": str(p),
            "manifest_sha256": hashlib.sha256(
                (p / "manifest.json").read_bytes()
            ).hexdigest(),
        }
        for name, p in references.items()
    },
}
(root / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
qualification = root / "qualification"
qualification.mkdir()
for scenario, step in protocol["scenarios"].items():
    for variant in ["dense", "sparse"]:
        out = qualification / (scenario + "-" + variant)
        out.mkdir()
        cmd = [
            str(root / "model" / variant),
            "0",
            str(step),
            "10",
            "5000",
            "100",
            str(out / "observations.csv"),
            "830",
            "1",
            str(out / "traits.csv"),
        ]
        with (
            (out / "aggregate.csv").open("x") as stdout,
            (out / "stderr").open("x") as stderr,
        ):
            result = subprocess.run(cmd, stdout=stdout, stderr=stderr, timeout=120)
        (out / "exit.json").write_text(
            json.dumps({"command": cmd, "exit_code": result.returncode}) + "\n"
        )
        assert result.returncode == 0
    dense = qualification / (scenario + "-dense")
    sparse = qualification / (scenario + "-sparse")
    for name in ["aggregate.csv", "observations.csv"]:
        assert (dense / name).read_bytes() == (sparse / name).read_bytes()
    with (dense / "traits.csv").open() as f:
        expected = [
            r
            for r in csv.DictReader(f)
            if r["kind"] == "initial"
            or (
                r["kind"] == "joint"
                and (int(r["cycle"]) % 100 == 0 or int(r["cycle"]) == 1)
            )
        ]
    with (sparse / "traits.csv").open() as f:
        assert list(csv.DictReader(f)) == expected
(root / "qualification.json").write_text(
    json.dumps(
        {
            "complete_native_pairs": 2,
            "cycles_per_pair": 5000,
            "aggregate_and_individual_byte_exact": True,
            "sampled_joint_counts_exact": True,
        }
    )
    + "\n"
)
started = time.monotonic()
(root / "runs").mkdir()


def execute(job):
    """Execute one original seed and check its complete recorded trajectory."""
    scenario, seed = job
    remaining = int(3600 - (time.monotonic() - started))
    assert remaining > 0, "Global execution bound exhausted"
    out = root / "runs" / f"{scenario}-{seed}"
    out.mkdir()
    cmd = [
        str(root / "model/sparse"),
        str(seed),
        str(protocol["scenarios"][scenario]),
        "10",
        "100000",
        "100",
        str(out / "observations.csv"),
        "830",
        "1",
        str(out / "traits.csv"),
    ]
    before = time.monotonic()
    with (
        (out / "aggregate.csv").open("x") as stdout,
        (out / "stderr").open("x") as stderr,
    ):
        result = subprocess.run(
            cmd, stdout=stdout, stderr=stderr, timeout=min(300, remaining)
        )
    (out / "exit.json").write_text(
        json.dumps(
            {
                "command": cmd,
                "exit_code": result.returncode,
                "elapsed_seconds": time.monotonic() - before,
            }
        )
        + "\n"
    )
    assert result.returncode == 0
    with (out / "aggregate.csv").open() as f:
        rows = list(csv.DictReader(f))
    final = int(rows[-1]["cycle"])
    assert final == 100000 or int(rows[-1]["population"]) == 0
    assert [int(r["cycle"]) for r in rows] == sorted(
        {1, final, *range(100, final + 1, 100)}
    )
    assert all(int(r["conservation_error"]) == 0 for r in rows)
    reference = references[scenario] / "runs" / str(seed) / "aggregate.csv"
    assert (
        hashlib.sha256(reference.read_bytes()).hexdigest()
        == reference_records[scenario][seed]["sha256"]["aggregate.csv"]
    )
    with reference.open() as f:
        expected = [
            r
            for r in csv.DictReader(f)
            if int(r["cycle"]) in {1, 100, 200, 300, 400, 500}
        ]
    assert [r for r in rows if int(r["cycle"]) <= 500] == expected
    populations = {int(r["cycle"]): int(r["population"]) for r in rows}
    joint = {}
    with (out / "traits.csv").open() as f:
        for r in csv.DictReader(f):
            assert int(r["infertility"]) in range(
                protocol["scenarios"][scenario],
                11 * protocol["scenarios"][scenario],
                protocol["scenarios"][scenario],
            )
            assert int(r["birth_cost"]) in range(0, 91, 10)
            if r["kind"] == "joint":
                cycle = int(r["cycle"])
                joint[cycle] = joint.get(cycle, 0) + int(r["count"])
    assert joint.pop(0) == 830
    assert all(joint.get(cycle, 0) == count for cycle, count in populations.items())
    return {
        "scenario": scenario,
        "seed": seed,
        "final_cycle": final,
        "final_population": int(rows[-1]["population"]),
        "observations": len(rows),
        "sha256": {
            p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in out.iterdir()
        },
    }


with (
    ThreadPoolExecutor(max_workers=4) as pool,
    (root / "completed.jsonl").open("x") as ledger,
):
    for record in pool.map(
        execute,
        [(scenario, seed) for seed in range(100) for scenario in protocol["scenarios"]],
    ):
        ledger.write(json.dumps(record) + "\n")
        ledger.flush()
(root / "complete.json").write_text(
    json.dumps({"complete_runs": 200, "elapsed_seconds": time.monotonic() - started})
    + "\n"
)
