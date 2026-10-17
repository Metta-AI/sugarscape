"""Independently audit sealed native Criterion timing checkpoints from raw samples."""

import argparse
import hashlib
import json
import re
from pathlib import Path

import numpy as np

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument(
    "checkpoint", type=Path, help="Extracted checkpoint containing results/"
)
parser.add_argument("output", type=Path, help="New audit directory")
args = parser.parse_args()
root = args.checkpoint / "results"
assets = Path(__file__).resolve().parent
manifest = json.loads((root / "manifest.json").read_text())
assert manifest["protocol"] == json.loads((assets / "protocol.json").read_text())
assert (
    manifest["source_sha256"]
    == json.loads((assets / "revision-fidelity.json").read_text())["hashes"]["timing"]
)
assert float(manifest["hardware"]["cpu_limit"]) == 8
hardware = manifest["hardware"]
affinity = hardware["affinity"]
assert len(affinity) == len(set(affinity)) == 8
allocated = set()
for segment in (
    hardware["cgroups"]["/sys/fs/cgroup/cpuset.cpus.effective"].strip().split(",")
):
    endpoints = [int(value) for value in segment.split("-")]
    assert 1 <= len(endpoints) <= 2
    allocated.update(range(endpoints[0], endpoints[-1] + 1))
assert allocated == set(affinity)
quota, period = hardware["cgroups"]["/sys/fs/cgroup/cpu.max"].split()
assert int(period) > 0
assert quota == "max" or int(quota) / int(period) >= 8
cpu_fields = {row["field"]: row["data"] for row in hardware["lscpu"]["lscpu"]}
assert int(cpu_fields["Thread(s) per core:"]) == 1

assert set(manifest["binary_sha256"]) == {"seq", "io", "tvar", "tarray"}
assert all(
    re.fullmatch(r"[0-9a-f]{64}", digest)
    for digest in manifest["binary_sha256"].values()
)
schedule = manifest["schedule"]
expected = {(6, "seq", 1, 500)}
expected |= {
    (6, variant, caps, 500)
    for variant in ("io", "tvar", "tarray")
    for caps in range(1, 9)
}
expected |= {
    (8, variant, 1 if variant == "seq" else 4, n)
    for variant in ("seq", "io", "tvar", "tarray")
    for n in (500, 1000, 1500, 2000, 2500)
}
assert len(schedule) == len(expected) == 45
assert {
    (c["table"], c["variant"], c["caps"], c["agents"]) for c in schedule
} == expected
assert [c["table"] for c in schedule] == [6] * 25 + [8] * 20
progress = json.loads((root / "progress.json").read_text())
assert 0 < len(progress) <= 45
ledger = [
    json.loads(line) for line in (root / "attempts.jsonl").read_text().splitlines()
]
assert ledger == [
    attempt for condition in progress for attempt in condition["attempts"]
]
rows = []
files = {"manifest.json", "progress.json", "attempts.jsonl"}
for ordinal, condition in enumerate(progress):
    spec = schedule[ordinal]
    assert condition["ordinal"] == ordinal and condition["condition"] == spec
    variant, caps, agents = spec["variant"], spec["caps"], spec["agents"]
    if spec["table"] == 6:
        name = (
            "sugarscape-seq-singlecore/500"
            if variant == "seq"
            else f"sugarscape-{variant}-normal:{caps}/500"
        )
    else:
        name = (
            f"sugarscape-{variant}-rebirthing"
            + ("" if variant == "seq" else ":4")
            + f"/{agents}"
        )
    assert spec["benchmark"] == name
    attempts = condition["attempts"]
    assert 1 <= len(attempts) <= 3
    assert not any(row["accepted"] for row in attempts[:-1])
    assert condition["accepted"] == attempts[-1]["accepted"]
    assert condition["accepted"] or len(attempts) == 3
    for number, record in enumerate(attempts, 1):
        assert (
            record["ordinal"] == ordinal
            and record["condition"] == spec
            and record["attempt"] == number
        )
        folder = root / f"{ordinal:02d}-{variant}-{caps}-{agents}-attempt{number}"
        command = json.loads((folder / "command.json").read_text())
        runtime = [] if variant == "seq" else ["+RTS", f"-N{caps}", "-RTS"]
        assert Path(command[0]).name == f"sugarscape-{variant}"
        assert command[1:4] == ["--match", "prefix", name]
        assert command[4] == "--output" and command[6] == "--json"
        assert (
            Path(command[5]).name == "report.html"
            and Path(command[7]).name == "report.json"
        )
        assert command[8:] == runtime
        assert json.loads((folder / "exit.json").read_text())["exit_code"] == 0
        content = (folder / "report.html").read_bytes()
        assert hashlib.sha256(content).hexdigest() == record["report_sha256"]
        reports = json.loads(re.search(r"var reports = (.*);", content.decode())[1])
        assert len(reports) == 1 and reports[0]["reportName"] == name
        report = reports[0]
        samples = np.asarray(
            [
                [sample[report["reportKeys"].index(key)] for key in ("iters", "time")]
                for sample in report["reportMeasured"]
            ],
            dtype=float,
        )
        assert samples[:, 0].tolist() == [1, 2, 3, 4]
        assert np.isfinite(samples).all() and (samples[:, 1] > 0).all()
        design = np.column_stack((np.ones(4), samples[:, 0]))
        intercept, slope = np.linalg.lstsq(design, samples[:, 1], rcond=None)[0]
        residual = samples[:, 1] - design @ [intercept, slope]
        r_squared = float(
            1
            - residual @ residual / np.sum((samples[:, 1] - samples[:, 1].mean()) ** 2)
        )
        regression = report["reportAnalysis"]["anRegress"][0]
        assert abs(slope - regression["regCoeffs"]["iters"]["estPoint"]) < 1e-9
        assert abs(slope - record["ols_seconds"]) < 1e-9
        assert abs(r_squared - regression["regRSquare"]["estPoint"]) < 1e-12
        assert abs(r_squared - record["r_squared"]) < 1e-12
        assert record["accepted"] == (r_squared >= 0.99)
        std = float(np.std(samples[:, 1] / samples[:, 0], ddof=1))
        assert abs(std - report["reportAnalysis"]["anStdDev"]["estPoint"]) < 1e-9
        rows.append(
            {
                "ordinal": ordinal,
                "condition": spec,
                "attempt": number,
                "accepted": record["accepted"],
                "raw_samples": samples.tolist(),
                "ols_seconds": float(slope),
                "r_squared": r_squared,
                "sample_standard_deviation_seconds": std,
                "slope_error": abs(float(slope) - record["ols_seconds"]),
                "r_squared_error": abs(r_squared - record["r_squared"]),
                "report_sha256": record["report_sha256"],
            }
        )
        files |= {
            str(path.relative_to(root)) for path in folder.iterdir() if path.is_file()
        }
assert len(list(root.glob("*-attempt*/report.html"))) == len(rows)
summary = {
    "conditions_audited": len(progress),
    "conditions_required": 45,
    "attempts_audited": len(rows),
    "raw_measurements": 4 * len(rows),
    "conditions_accepted": sum(c["accepted"] for c in progress),
    "complete_grid": len(progress) == 45 and all(c["accepted"] for c in progress),
    "max_slope_error": max(row["slope_error"] for row in rows),
    "max_r_squared_error": max(row["r_squared_error"] for row in rows),
    "missing_conditions": schedule[len(progress) :],
    "hardware_allocation": {
        "affinity": affinity,
        "effective_cpuset": sorted(allocated),
        "cpu_max": hardware["cgroups"]["/sys/fs/cgroup/cpu.max"].strip(),
        "model": cpu_fields["Model name:"],
        "threads_per_core": int(cpu_fields["Thread(s) per core:"]),
        "limitation": "OS-reported topology and allocation only. This does not prove exclusive host use or fixed clock frequency.",
    },
    "scope": "Independent raw-measurement audit on different hardware; not a paper performance verdict. Source and binary hashes are recorded provenance, not independent binary reconstruction.",
    "rows": rows,
}
args.output.mkdir(parents=True, exist_ok=False)
(args.output / "audit.json").write_text(json.dumps(summary, indent=2) + "\n")
(args.output / "input-sha256.json").write_text(
    json.dumps(
        {
            name: hashlib.sha256((root / name).read_bytes()).hexdigest()
            for name in sorted(files)
        },
        indent=2,
    )
    + "\n"
)
print(
    json.dumps(
        {
            key: value
            for key, value in summary.items()
            if key not in ("rows", "missing_conditions")
        }
    )
)
