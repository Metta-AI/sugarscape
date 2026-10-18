"""Run the printed Figure 6(a) subsistence cases after metabolism-three parity."""

import argparse
from concurrent.futures import ThreadPoolExecutor
import csv
import difflib
import hashlib
import json
from pathlib import Path
import subprocess
import time

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("output", type=Path)
args = parser.parse_args()
root = args.output.resolve()
root.mkdir(exist_ok=False)
repo = Path(__file__).resolve().parent
protocol = {
    "target": "Figure6(a), independent conditional reconstruction",
    "infertility": [5, 10],
    "birth_cost": 0,
    "metabolism": 4,
    "puberty": 1,
    "initial_population": 1,
    "cycles": 505,
    "record_every": 1,
    "seeds": list(range(100)),
    "workers": 2,
    "per_run_seconds": 60,
    "global_seconds": 900,
    "analysis": "Compare observed actual-curve vertices against pointwise seed means and2.5/97.5percentiles. Visible0..200 and retained export201..505 reported separately. No interpolation, fitted seeds or equivalence criterion. Unknown paper seed and cycle-origin convention remain unresolved.",
    "qualification": "Both infertility cases, seed0,1000cycles: generalized engine at metabolism3 must equal pinned fixed engine byte-for-byte in aggregate and individual outputs.",
}
(root / "protocol.json").write_text(json.dumps(protocol, indent=2) + "\n")
original = (repo / "simulate.cpp").read_text()
assert (
    hashlib.sha256(original.encode()).hexdigest()
    == "17803df8b61cfded16718e4895cf574cae77aa514e57a79f99413d7173d49fbc"
)
source = original
for before, after in [
    ("if (argc != 7)", "if (argc != 8)"),
    ("record-every observations.csv", "record-every observations.csv metabolism"),
    (
        "    std::mt19937_64 random(seed);",
        '    const int metabolism_rate = std::stoi(argv[7]);\n    if (metabolism_rate != 3 && metabolism_rate != 4) throw std::invalid_argument("Invalid metabolism");\n    std::mt19937_64 random(seed);',
    ),
    ("agent.wealth < 3", "agent.wealth < metabolism_rate"),
    ("agent.wealth -= 3", "agent.wealth -= metabolism_rate"),
    ("metabolism += 3", "metabolism += metabolism_rate"),
]:
    assert source.count(before) == 1, before
    source = source.replace(before, after)
(root / "simulate.cpp").write_text(original)
(root / "simulate_subsistence.cpp").write_text(source)
(root / "metabolism.patch").write_text(
    "".join(
        difflib.unified_diff(
            original.splitlines(True),
            source.splitlines(True),
            fromfile="simulate.cpp",
            tofile="simulate_subsistence.cpp",
        )
    )
)
(root / "run_subsistence.py").write_bytes(Path(__file__).read_bytes())
for variant, filename in [
    ("fixed", "simulate.cpp"),
    ("generalized", "simulate_subsistence.cpp"),
]:
    subprocess.run(
        [
            "clang++",
            "-std=c++17",
            "-O2",
            "-Wall",
            "-Wextra",
            "-Werror",
            str(root / filename),
            "-o",
            str(root / variant),
        ],
        check=True,
    )
(root / "manifest.json").write_text(
    json.dumps(
        {
            "compiler": subprocess.check_output(["clang++", "--version"], text=True),
            "sha256": {
                p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                for p in root.iterdir()
                if p.is_file()
            },
        },
        indent=2,
    )
    + "\n"
)
(root / "qualification").mkdir()
for f in [5, 10]:
    for variant in ["fixed", "generalized"]:
        target = root / "qualification" / f"{f}-{variant}"
        target.mkdir()
        cmd = [
            str(root / variant),
            "0",
            str(f),
            "0",
            "1000",
            "1",
            str(target / "observations.csv"),
        ] + (["3"] if variant == "generalized" else [])
        with (
            (target / "aggregate.csv").open("x") as out,
            (target / "stderr").open("x") as err,
        ):
            p = subprocess.run(cmd, stdout=out, stderr=err, timeout=60)
        (target / "exit.json").write_text(
            json.dumps({"command": cmd, "exit_code": p.returncode}) + "\n"
        )
        assert p.returncode == 0
    for filename in ["aggregate.csv", "observations.csv"]:
        assert (root / "qualification" / f"{f}-fixed" / filename).read_bytes() == (
            root / "qualification" / f"{f}-generalized" / filename
        ).read_bytes()
(root / "qualification.json").write_text(
    json.dumps(
        {
            "complete_native_pairs": 2,
            "cycles_per_pair": 1000,
            "aggregate_and_individual_outputs_byte_exact": True,
        }
    )
    + "\n"
)
(root / "runs").mkdir()
started = time.monotonic()


def execute(job):
    """Execute one complete printed parameter case and retain terminal evidence."""
    infertility, seed = job
    remaining = int(900 - (time.monotonic() - started))
    assert remaining > 0
    target = root / "runs" / f"{infertility}-{seed}"
    target.mkdir()
    cmd = [
        str(root / "generalized"),
        str(seed),
        str(infertility),
        "0",
        "505",
        "1",
        str(target / "observations.csv"),
        "4",
    ]
    before = time.monotonic()
    with (
        (target / "aggregate.csv").open("x") as out,
        (target / "stderr").open("x") as err,
    ):
        p = subprocess.run(cmd, stdout=out, stderr=err, timeout=min(remaining, 60))
    (target / "exit.json").write_text(
        json.dumps(
            {
                "command": cmd,
                "exit_code": p.returncode,
                "elapsed_seconds": time.monotonic() - before,
            }
        )
        + "\n"
    )
    assert p.returncode == 0
    with (target / "aggregate.csv").open() as stream:
        rows = list(csv.DictReader(stream))
    assert [int(r["cycle"]) for r in rows] == list(range(1, len(rows) + 1))
    assert len(rows) == 505 or int(rows[-1]["population"]) == 0
    assert all(int(r["conservation_error"]) == 0 for r in rows)
    return {
        "infertility": infertility,
        "seed": seed,
        "cycles": len(rows),
        "final_population": int(rows[-1]["population"]),
        "sha256": {
            p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in target.iterdir()
        },
    }


with (
    ThreadPoolExecutor(max_workers=2) as pool,
    (root / "completed.jsonl").open("x") as ledger,
):
    for record in pool.map(
        execute, [(f, seed) for f in [5, 10] for seed in range(100)]
    ):
        ledger.write(json.dumps(record) + "\n")
        ledger.flush()
(root / "complete.json").write_text(
    json.dumps({"complete_runs": 200, "elapsed_seconds": time.monotonic() - started})
    + "\n"
)
