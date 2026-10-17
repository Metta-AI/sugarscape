"""Reconcile independently audited culture intervals without rewriting their ledgers."""

import argparse
import hashlib
import json
from pathlib import Path

from scipy import stats

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("original_protocol", type=Path)
parser.add_argument("continuation_protocol", type=Path)
parser.add_argument("audits", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
original = json.loads(args.original_protocol.read_text())
continuation = json.loads(args.continuation_protocol.read_text())
assert set(continuation) == set(original) | {"retained_prefix"}
for key in original:
    if key not in {"purpose", "scenarios", "limits"}:
        assert original[key] == continuation[key], key
assert continuation["scenarios"] == [
    scenario for scenario in original["scenarios"] if scenario["key"] == "culture"
]
assert set(original["limits"]) == set(continuation["limits"])
for key in original["limits"]:
    if key != "seconds_per_worker":
        assert original["limits"][key] == continuation["limits"][key], key
report = {
    "scope": "Complete frozen culture cohort; global ratios do not establish spatial hill dominance. No whole-paper credit.",
    "variants": {},
    "inputs_sha256": {},
}
for variant in ["original", "corrected"]:
    prefix = continuation["retained_prefix"][variant]
    assert prefix["interval"] == [0, 33]
    assert prefix["completed_culture_inputs"] == 33
    assert prefix["terminal_state"]["Running"] is False
    results = []
    for segment, interval, protocol_path in [
        ("retained", range(33), args.original_protocol),
        ("remaining", range(33, 100), args.continuation_protocol),
    ]:
        folder = args.audits / f"{variant}-{segment}-audit-001"
        audit_path = folder / "audit.json"
        ledger_path = folder / "ledger-snapshot.jsonl"
        audit = json.loads(audit_path.read_text())
        protocol_hash = hashlib.sha256(protocol_path.read_bytes()).hexdigest()
        ledger_hash = hashlib.sha256(ledger_path.read_bytes()).hexdigest()
        assert audit["variant"] == variant and audit["scenario"] == "culture"
        assert audit["protocol_sha256"] == protocol_hash
        assert audit["ledger_snapshot_sha256"] == ledger_hash
        if segment == "retained":
            assert prefix["ledger_sha256"] == ledger_hash
            assert prefix["protocol_sha256"] == protocol_hash
        records = [json.loads(line) for line in ledger_path.read_text().splitlines()]
        records = [record for record in records if record["scenario"] == "culture"]
        assert [record["index"] for record in records] == list(interval)
        assert [row["index"] for row in audit["results"]] == list(interval)
        assert audit["validated_runs"] == len(interval)
        for row, record in zip(audit["results"], records, strict=True):
            assert row["seed"] == record["seed"] == original["seeds"][row["index"]]
            assert (
                row["source_record_sha256"]
                == hashlib.sha256(
                    json.dumps(record, sort_keys=True).encode()
                ).hexdigest()
            )
            assert row["steps"] == 2700 and row["summary_observations"] == 2701
        results.extend(audit["results"])
        for path in [audit_path, ledger_path]:
            report["inputs_sha256"][str(path.relative_to(args.audits))] = (
                hashlib.sha256(path.read_bytes()).hexdigest()
            )
    assert [row["index"] for row in results] == list(range(100))
    assert len({row["seed"] for row in results}) == 100
    comparisons = []
    assert all(row["predicates"] for row in results), (
        "Undefined ratios require explicit analysis"
    )
    for predicate in results[0]["predicates"]:
        passes = sum(row["predicates"][predicate] for row in results)
        comparisons.append(
            {
                "predicate": predicate,
                "passes": passes,
                "n": 100,
                "exact_binomial_ci95": [
                    float(stats.beta.ppf(0.025, passes, 101 - passes))
                    if passes
                    else 0.0,
                    float(stats.beta.ppf(0.975, passes + 1, 100 - passes))
                    if passes < 100
                    else 1.0,
                ],
            }
        )
    report["variants"][variant] = {
        "validated_runs": 100,
        "summary_observations": sum(row["summary_observations"] for row in results),
        "snapshot_agent_observations": sum(
            row["snapshot_agent_observations"] for row in results
        ),
        "extinction_count": sum(row["extinct"] for row in results),
        "comparisons": comparisons,
        "results": results,
    }
for name, path in [
    ("original_protocol", args.original_protocol),
    ("continuation_protocol", args.continuation_protocol),
]:
    report["inputs_sha256"][name] = hashlib.sha256(path.read_bytes()).hexdigest()
with args.output.open("x") as output:
    output.write(json.dumps(report, indent=2, allow_nan=False) + "\n")
print(
    json.dumps(
        {
            variant: {key: value for key, value in result.items() if key != "results"}
            for variant, result in report["variants"].items()
        }
    )
)
