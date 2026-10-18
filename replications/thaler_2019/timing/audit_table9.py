"""Audit the complete six-condition Table9 timings and thirty native retry processes."""

import argparse
import hashlib
import json
import re
import random
import tarfile
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
assert manifest["protocol"] == json.loads((assets / "table9-protocol.json").read_text())
assert (
    manifest["source_sha256"]
    == json.loads((assets / "revision-fidelity.json").read_text())["hashes"]["timing"]
)
assert float(manifest["hardware"]["cpu_limit"]) == 64
hardware = manifest["hardware"]
affinity = hardware["affinity"]
assert len(affinity) == len(set(affinity)) == 64
allocated = set()
for segment in (
    hardware["cgroups"]["/sys/fs/cgroup/cpuset.cpus.effective"].strip().split(",")
):
    endpoints = [int(value) for value in segment.split("-")]
    assert 1 <= len(endpoints) <= 2
    allocated.update(range(endpoints[0], endpoints[-1] + 1))
assert allocated == set(affinity)
for path, value in hardware["cgroups"].items():
    if path.endswith("/cpu.max"):
        quota, period = value.split()
        assert int(period) > 0
        assert quota == "max" or int(quota) / int(period) >= 64
cpu_fields = {row["field"]: row["data"] for row in hardware["lscpu"]["lscpu"]}
assert int(cpu_fields["Thread(s) per core:"]) == 2

assert set(manifest["binary_sha256"]) == {"tarray"}
assert all(
    re.fullmatch(r"[0-9a-f]{64}", digest)
    for digest in manifest["binary_sha256"].values()
)
archive_path = args.checkpoint / "source-f5851488.tar.gz"
assert (
    hashlib.sha256(archive_path.read_bytes()).hexdigest()
    == "69166a06218a0177fc9da80e1e82b9e759843041fbb36cd515c2647e76538ab0"
)
with tarfile.open(archive_path) as archive:
    for name, digest in manifest["source_sha256"].items():
        assert archive.getmember(name).isfile()
        assert hashlib.sha256(archive.extractfile(name).read()).hexdigest() == digest
schedule = manifest["schedule"]
expected_schedule = [
    dict(c, table=9, caps=c["capabilities"], scenario=c["variant"], variant="tarray")
    for c in json.loads((assets / "table9-preflight.json").read_text())["conditions"]
]
random.Random(20261018).shuffle(expected_schedule)
assert schedule == expected_schedule
expected = {(9, "tarray", caps, n) for caps in (16, 32, 64) for n in (500, 2500)}
assert len(schedule) == len(expected) == 6
assert {
    (c["table"], c["variant"], c["caps"], c["agents"]) for c in schedule
} == expected
assert int((args.checkpoint / "exit-code.txt").read_text()) == 0
assert (
    hashlib.sha256((root / "tarray-timing-binary").read_bytes()).hexdigest()
    == manifest["binary_sha256"]["tarray"]
)
progress = json.loads((root / "progress.json").read_text())
assert 0 < len(progress) == 6
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
    scenario = "normal" if agents == 500 else "rebirthing"
    name = f"sugarscape-tarray-{scenario}:{caps}/{agents}"
    assert spec["scenario"] == scenario and spec["capabilities"] == caps
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
        assert Path(command[0]).name == "tarray-timing-binary"
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
    "conditions_required": 6,
    "attempts_audited": len(rows),
    "raw_measurements": 4 * len(rows),
    "conditions_accepted": sum(c["accepted"] for c in progress),
    "complete_grid": len(progress) == 6 and all(c["accepted"] for c in progress),
    "max_slope_error": max(row["slope_error"] for row in rows),
    "max_r_squared_error": max(row["r_squared_error"] for row in rows),
    "missing_conditions": schedule[len(progress) :],
    "hardware_allocation": {
        "affinity": affinity,
        "effective_cpuset": sorted(allocated),
        "cgroups": hardware["cgroups"],
        "model": cpu_fields["Model name:"],
        "threads_per_core": int(cpu_fields["Thread(s) per core:"]),
        "limitation": "OS-reported topology and allocation only. This does not prove exclusive host use or fixed clock frequency.",
    },
    "scope": "Independent raw-measurement audit on different hardware; not a paper performance verdict. Source and binary hashes are recorded provenance, not independent binary reconstruction.",
    "rows": rows,
}
terminal = json.loads((root / "terminal.json").read_text())
assert terminal == {
    "timing_conditions_accepted": 6,
    "timing_conditions_required": 6,
    "retry_processes_completed": 30,
    "retry_processes_required": 30,
    "complete": True,
}
assert summary["complete_grid"]
assert (
    hashlib.sha256((root / "retry-Main.hs").read_bytes()).hexdigest()
    == "cdea6f017ef1b91b4a1d6dd8590f4afc1c18b96694c57f612b7dae15d11b3b3f"
)
retry_digest = hashlib.sha256((root / "tarray-retry-binary").read_bytes()).hexdigest()
assert retry_digest == (root / "retry-binary-sha256.txt").read_text().strip()
assert retry_digest != manifest["binary_sha256"]["tarray"]
retry_schedule = json.loads((root / "retry-schedule.json").read_text())
assert len(retry_schedule) == 30
expected_retry_order = [dict(c, repetition=r) for c in schedule for r in range(5)]
random.Random(20261019).shuffle(expected_retry_order)
assert retry_schedule == expected_retry_order
expected_retries = {(c["benchmark"], rep) for c in schedule for rep in range(5)}
assert {(c["benchmark"], c["repetition"]) for c in retry_schedule} == expected_retries
retry_ledger = [
    json.loads(line)
    for line in (root / "retry-completed.jsonl").read_text().splitlines()
]
assert len(retry_ledger) == 30
for index, record in enumerate(retry_ledger):
    condition = retry_schedule[index]
    assert record["index"] == index and record["condition"] == condition
    folder = root / f"retry-{index:02d}"
    for filename, digest in record["files_sha256"].items():
        assert hashlib.sha256((folder / filename).read_bytes()).hexdigest() == digest
    assert int((folder / "exit-code.txt").read_text()) == 0
    command = json.loads((folder / "command.json").read_text())
    assert Path(command[0]).name == "tarray-retry-binary"
    assert command[1:] == [
        "--iters",
        "1",
        "--match",
        "prefix",
        condition["benchmark"],
        "+RTS",
        f"-N{condition['caps']}",
        "-RTS",
    ]
    assert (
        folder / "stdout.log"
    ).read_text().strip() == f"benchmarking {condition['benchmark']}"
    stderr = (folder / "stderr.log").read_text()
    counters = re.findall(
        r"^SugarScape\s+(\d+)\s+(\d+)\s+(\d+\.\d+)\s*$", stderr, re.MULTILINE
    )
    assert len(counters) == stderr.count("STM transaction statistics (") == 1
    commits, retries, printed = counters[0]
    commits, retries = int(commits), int(retries)
    assert commits > 0 and commits == record["commits"] and retries == record["retries"]
    assert (
        retries / commits == record["ratio"]
        and f"{retries / commits:.2f}" == printed == record["printed_ratio"]
    )
files |= {str(p.relative_to(root)) for p in root.glob("retry-*/*") if p.is_file()}
files |= {
    "retry-Main.hs",
    "tarray-timing-binary",
    "tarray-retry-binary",
    "retry-binary-sha256.txt",
    "retry-schedule.json",
    "retry-completed.jsonl",
    "terminal.json",
}
summary["retry_processes_audited"] = 30
summary["retry_records"] = retry_ledger
summary["scope"] = (
    "Complete Table9 raw-measurement and retry-counter audit on matching instance class. No historical clock/isolation equivalence or whole-paper verdict."
)
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
            if key not in ("rows", "missing_conditions", "retry_records")
        }
    )
)
