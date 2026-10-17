"""Reconcile the retained disease seed with independently audited remaining runs."""

import argparse
import ast
import csv
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys

from scipy import stats

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("protocol", type=Path)
parser.add_argument("native_home", type=Path)
parser.add_argument("first_audit", type=Path)
parser.add_argument("run", type=Path)
parser.add_argument("output", type=Path)
parser.add_argument("--allow-prefix", action="store_true")
parser.add_argument("--continuation", nargs="+", type=Path, default=[])
parser.add_argument("--interrupted-ledger", nargs="+", type=Path, default=[])
args = parser.parse_args()
interrupted = {}
for path in args.interrupted_ledger:
    receipt = json.loads(path.read_text())
    assert receipt["state"]["Status"] == "exited"
    assert receipt["state"]["Running"] is False and receipt["state"]["ExitCode"] != 0
    digest = receipt["ledger_sha256"]
    assert digest not in interrupted
    interrupted[digest] = hashlib.sha256(path.read_bytes()).hexdigest()
used_interrupted = set()
assert not args.output.exists()
protocol = json.loads(args.protocol.read_text())
manifest = json.loads((args.run / "manifest.json").read_text())
assert manifest["protocol"] == protocol and manifest["interval"] == [1, 100]
variant = manifest["variant"]
assert variant in ["disease_count_corrected", "combined_corrected"]
assert (
    len(protocol["seeds"])
    == len(set(protocol["seeds"]))
    == protocol["replications"]
    == 100
)
assert protocol["scenarios"] == [
    {
        "key": "disease_persist",
        "constructor": "mkParamsAnimationV_2",
        "steps": 1000,
        "stride": 50,
    }
]
spec = protocol["variants"][variant]
native = args.native_home / Path(spec["root"]).relative_to("/root/sugarscape")
for name, digest in spec["source_sha256"].items():
    assert hashlib.sha256((native / "source" / name).read_bytes()).hexdigest() == digest
for name, key in [("observe", "binary_sha256"), ("Observe.hs", "observer_sha256")]:
    assert hashlib.sha256((native / name).read_bytes()).hexdigest() == spec[key]
retained = protocol["retained_first_seed"][variant]
assert retained["index"] == 0 and retained["seed"] == protocol["seeds"][0]
assert retained["steps"] == 1000 and retained["stride"] == 50
assert (
    hashlib.sha256(args.first_audit.read_bytes()).hexdigest()
    == retained["audit_sha256"]
)
first_audit = json.loads(args.first_audit.read_text())
first = next(
    r
    for r in first_audit["results"]
    if r["variant"] == variant and r["case"] == "disease_persist"
)
assert first["binary_sha256"] == spec["binary_sha256"]
assert first["files_sha256"] == retained["files_sha256"]
first_root = args.native_home / Path(retained["root"]).relative_to("/root/sugarscape")
for name, digest in retained["files_sha256"].items():
    assert hashlib.sha256((first_root / name).read_bytes()).hexdigest() == digest
args.output.mkdir()
rows = []
inputs = [(0, first_root / "disease_persist", first)]
remaining_audits = []
commands = []
observations = first["agent_observations"]
for ordinal, run in enumerate([args.run, *args.continuation]):
    segment_manifest = json.loads((run / "manifest.json").read_text())
    assert (
        segment_manifest["protocol"] == protocol
        and segment_manifest["variant"] == variant
    )
    start, stop = segment_manifest["interval"]
    assert 1 <= start < stop <= 100
    ledger = (run / "completed.jsonl").read_bytes()
    digest = hashlib.sha256(ledger).hexdigest()
    records = [json.loads(line) for line in ledger.splitlines()]
    if digest in interrupted:
        assert len(records) < stop - start
        used_interrupted.add(digest)
    elif not args.allow_prefix:
        assert json.loads((run / "complete.json").read_text()) == {
            "completed_runs": stop - start
        }
    audit_output = args.output / f"remaining-audit-{ordinal:03d}"
    command = [
        sys.executable,
        str(Path(__file__).with_name("audit_observer_ensemble.py")),
        str(run),
        str(args.protocol),
        "disease_persist",
        str(audit_output),
        "--interval",
        str(start),
        str(stop),
        "--recorded-run-name",
        run.name,
    ]
    if args.allow_prefix or digest in interrupted:
        command.append("--allow-prefix")
    subprocess.run(command, check=True)
    commands.append(command)
    remaining = json.loads((audit_output / "audit.json").read_text())
    assert remaining["variant"] == variant and remaining["comparisons"] == []
    observations += remaining["snapshot_agent_observations"]
    remaining_audits.append(
        {
            "directory": audit_output.name,
            "sha256": hashlib.sha256(
                (audit_output / "audit.json").read_bytes()
            ).hexdigest(),
        }
    )
    inputs.extend(
        (
            r["index"],
            run / "disease_persist" / f"{r['index']:03d}-{r['seed']}" / "trajectory",
            r,
        )
        for r in remaining["results"]
    )
assert used_interrupted == set(interrupted), "Unused interrupted-ledger receipt"
assert [index for index, _, _ in inputs] == list(range(len(inputs)))
for index, prefix, audited in inputs:
    seed = protocol["seeds"][index]
    assert audited["seed"] == seed
    text = Path(str(prefix) + ".scenario.txt").read_text()
    assert text.startswith(f"Constructor: mkParamsAnimationV_2\nSeed: {seed}\n")
    declaration = next(
        line
        for line in text.splitlines()
        if line.startswith("E rule active (disease):")
    )
    immune, count, maximum_length, initial, pool = ast.literal_eval(
        declaration.split("Just ", 1)[1]
    )
    assert (immune, count, maximum_length, initial) == (50, 25, 10, 10)
    assert len(pool) == 25 and all(1 <= len(disease) <= 10 for disease in pool)
    assert all(type(bit) is bool for disease in pool for bit in disease)
    summaries = list(csv.DictReader(Path(str(prefix) + ".summary.csv").open()))
    assert [int(r["time"]) for r in summaries] == list(range(1001))
    assert all(math.isfinite(float(v)) for r in summaries for v in r.values())
    assert all(0 <= int(r["infected"]) <= int(r["population"]) for r in summaries)
    population, infected = (
        int(summaries[-1][key]) for key in ["population", "infected"]
    )
    assert (population, infected) == (
        audited["final_population"],
        audited["final_infected"],
    )
    rows.append(
        {
            "index": index,
            "seed": seed,
            "final_population": population,
            "final_infected": infected,
            "distinct_diseases": len(set(map(tuple, pool))),
            "disease_lengths": list(map(len, pool)),
            "first_zero_infected_with_survivors": next(
                (
                    int(r["time"])
                    for r in summaries
                    if int(r["time"]) > 0
                    and int(r["population"]) > 0
                    and int(r["infected"]) == 0
                ),
                None,
            ),
            "predicates": {
                "source_above_ceil_half": infected > math.ceil(population / 2),
                "prose_strict_majority": 2 * infected > population,
            },
            "configuration_sha256": hashlib.sha256(
                Path(str(prefix) + ".scenario.txt").read_bytes()
            ).hexdigest(),
        }
    )
assert args.allow_prefix or len(rows) == 100
comparisons = []
if not args.allow_prefix:
    for predicate in rows[0]["predicates"]:
        passes = sum(r["predicates"][predicate] for r in rows)
        interval = stats.binomtest(passes, 100).proportion_ci(
            confidence_level=0.95, method="exact"
        )
        comparisons.append(
            {
                "predicate": predicate,
                "passes": passes,
                "n": 100,
                "exact_binomial_ci95": [float(interval.low), float(interval.high)],
            }
        )
report = {
    "variant": variant,
    "validated_runs": len(rows),
    "complete_ensemble": not args.allow_prefix,
    "protocol_sha256": hashlib.sha256(args.protocol.read_bytes()).hexdigest(),
    "retained_first_audit_sha256": retained["audit_sha256"],
    "remaining_audits": remaining_audits,
    "interrupted_ledger_receipts": interrupted,
    "snapshot_agent_observations": observations,
    "extinction_count": sum(r["final_population"] == 0 for r in rows),
    "zero_infected_final_count": sum(r["final_infected"] == 0 for r in rows),
    "results": rows,
    "comparisons": comparisons,
    "scope": "Corrected 25-entry disease pools, not necessarily 25 distinct diseases. Prefixes emit no inference; no full-paper verdict.",
}
(args.output / "audit.json").write_text(
    json.dumps(report, indent=2, allow_nan=False) + "\n"
)
(args.output / "remaining-audit-command.json").write_text(
    json.dumps(commands, indent=2) + "\n"
)
print(json.dumps({k: v for k, v in report.items() if k != "results"}))
