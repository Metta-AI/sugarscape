"""Validate all ten complete cohorts before adjusting the declared 30 comparisons."""

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("run", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
assert not args.output.exists()
plan = json.loads((args.run / "plan.json").read_text())
assert len(plan["original_rows_zero_based"]) == 10
assert len(set(plan["original_rows_zero_based"])) == 10
assert plan["total_runs"] == 1280
assert plan["seeds_per_engine"] == 64
assert plan["observations_per_run"] == 501
for filename, digest in json.loads(
    (args.run / "frozen-sha256.json").read_text()
).items():
    assert hashlib.sha256(Path(filename).read_bytes()).hexdigest() == digest
complete = json.loads((args.run / "dispatch-complete.json").read_text())
assert complete["cohorts_attempted"] == 10
ledger = [
    json.loads(line) for line in (args.run / "cohorts.jsonl").read_text().splitlines()
]
assert [row["original_row"] for row in ledger] == plan["original_rows_zero_based"]
assert all(row["exit_code"] in [0, 1] for row in ledger)
cohort_paths = {}
recovery_records = []
cohorts = []
tests = []
for index in plan["original_rows_zero_based"]:
    original = args.run / f"row-{index}"
    terminal = next(row for row in ledger if row["original_row"] == index)
    cohort = original
    comparison_directory = "comparison.json"
    if terminal["exit_code"] == 1:
        cohort = args.run / f"row-{index}-reconciled-001"
        recovery = args.run / f"row-{index}-recovery-001"
        reconciliation = json.loads((cohort / "reconciliation.json").read_text())
        recovery_plan_bytes = (recovery / "plan.json").read_bytes()
        recovery_plan = json.loads(recovery_plan_bytes)
        assert reconciliation["original_terminal"] == terminal
        assert not (original / "complete.json").exists()
        interrupted_seed = recovery_plan["interrupted_seed"]
        assert (
            hashlib.sha256(
                (original / "independent" / f"row-{interrupted_seed}.csv").read_bytes()
            ).hexdigest()
            == reconciliation[f"interrupted_seed{interrupted_seed}_sha256"]
        )
        assert recovery_plan["original_row"] == index
        assert recovery_plan["original_cohort"] == str(original)
        assert (
            recovery_plan["original_protocol_sha256"]
            == hashlib.sha256((original / "protocol.json").read_bytes()).hexdigest()
        )
        assert (
            reconciliation["recovery_plan_sha256"]
            == hashlib.sha256(recovery_plan_bytes).hexdigest()
        )
        assert reconciliation["original_receipts"] == [
            json.loads(line)
            for line in (original / "completed.jsonl").read_text().splitlines()
        ]
        assert reconciliation["recovery_receipts"] == [
            json.loads(line)
            for line in (recovery / "completed.jsonl").read_text().splitlines()
        ]
        assert reconciliation["recovery_complete"] == json.loads(
            (recovery / "complete.json").read_text()
        )
        assert reconciliation["recovery_complete"]["exit_code"] == 0
        assert reconciliation["recovery_complete"]["independent_runs"] == len(
            recovery_plan["remaining_independent_seeds"]
        )
        commands = dict(json.loads((original / "commands.json").read_text()))
        for receipt in reconciliation["recovery_receipts"]:
            expected_command = commands[f"independent-{receipt['seed']}"][:]
            expected_command[-1] = str(
                recovery / "independent" / f"row-{receipt['seed']}.csv"
            )
            assert receipt["command"] == expected_command
        assert (
            reconciliation["recovery_complete"]["elapsed_seconds"]
            <= recovery_plan["wall_limit_seconds"]
        )
        for name, digest in recovery_plan["input_sha256"].items():
            assert hashlib.sha256(Path(name).read_bytes()).hexdigest() == digest
        original_seeds = recovery_plan["completed_independent_seeds"]
        remaining_seeds = recovery_plan["remaining_independent_seeds"]
        assert original_seeds + remaining_seeds == list(range(64))
        assert [row["name"] for row in reconciliation["original_receipts"]] == [
            "native"
        ] + [f"independent-{seed}" for seed in original_seeds]
        assert [
            row["seed"] for row in reconciliation["recovery_receipts"]
        ] == remaining_seeds
        assert all(
            row["exit_code"] == 0
            for row in reconciliation["original_receipts"]
            + reconciliation["recovery_receipts"]
        )
        assert (cohort / "protocol.json").read_bytes() == (
            original / "protocol.json"
        ).read_bytes()
        expected_paths = {
            f"{engine}/row-{seed}.csv"
            for engine in ["native", "independent"]
            for seed in range(64)
        }
        assert set(reconciliation["trajectories"]) == expected_paths
        for name, receipt in reconciliation["trajectories"].items():
            engine, filename = name.split("/")
            seed = int(filename.removeprefix("row-").removesuffix(".csv"))
            source_cohort = (
                recovery
                if engine == "independent" and seed in remaining_seeds
                else original
            )
            assert receipt["source"] == str(source_cohort / name)
            assert (
                hashlib.sha256(Path(receipt["source"]).read_bytes()).hexdigest()
                == receipt["sha256"]
            )
            assert (
                hashlib.sha256((cohort / name).read_bytes()).hexdigest()
                == receipt["sha256"]
            )
        recovery_records.append(
            {
                "original_row": index,
                "original_terminal": terminal,
                "reconciliation_sha256": hashlib.sha256(
                    (cohort / "reconciliation.json").read_bytes()
                ).hexdigest(),
            }
        )
        comparison_directory = "comparison"
    cohort_paths[index] = cohort
    complete_cohort = json.loads((cohort / "complete.json").read_text())
    assert complete_cohort["exit_code"] == 0
    assert complete_cohort["native_runs"] == complete_cohort["independent_runs"] == 64
    receipts = [
        json.loads(line)
        for line in (cohort / "completed.jsonl").read_text().splitlines()
    ]
    assert [row["name"] for row in receipts] == ["native"] + [
        f"independent-{seed}" for seed in range(64)
    ]
    assert all(row["exit_code"] == 0 for row in receipts)
    protocol_bytes = (cohort / "protocol.json").read_bytes()
    protocol = json.loads(protocol_bytes)
    assert protocol["original_input_zero_based"] == index
    assert protocol["fresh_seeds"] == list(range(64))
    assert protocol["native_runs"] == protocol["independent_runs"] == 64
    audit = json.loads((cohort / "audit/audit.json").read_text())
    assert audit["runs"] == 128 and audit["observations"] == 64128
    assert audit["excluded_runs"] == 0
    assert audit["protocol_sha256"] == hashlib.sha256(protocol_bytes).hexdigest()
    expected = {
        f"{engine}/row-{seed}.csv"
        for engine in ["native", "independent"]
        for seed in range(64)
    }
    assert set(audit["trajectory_sha256"]) == expected
    for name, digest in audit["trajectory_sha256"].items():
        assert hashlib.sha256((cohort / name).read_bytes()).hexdigest() == digest
    comparison_bytes = (cohort / comparison_directory / "summary.json").read_bytes()
    comparison = json.loads(comparison_bytes)
    assert (
        comparison["inputs_sha256"]
        == hashlib.sha256((cohort / "audit/runs.csv").read_bytes()).hexdigest()
    )
    assert comparison["protocol_sha256"] == audit["protocol_sha256"]
    assert comparison["seeds_per_engine"] == 64 and comparison["excluded_runs"] == 0
    assert (
        comparison["permutations"] == 19999
        and comparison["permutation_seed"] == 20261019
    )
    assert (
        comparison["joint_monte_carlo_p_plus_one"]
        == (comparison["joint_exceedances"] + 1) / 20000
    )
    assert comparison["joint_maximum_ecdf_difference"] == max(
        row["ecdf_maximum_difference"] for row in comparison["metrics"]
    )
    tests.append(
        {
            "original_row": index,
            "test": "joint_six_metrics",
            "raw_p": comparison["joint_monte_carlo_p_plus_one"],
        }
    )
    for event in ["persistent_late_price", "low_final_population"]:
        tests.append(
            {
                "original_row": index,
                "test": event,
                "raw_p": comparison["rare_events"][event]["two_sided_fisher_p"],
            }
        )
    cohorts.append(
        {
            "original_row": index,
            "parameters": protocol["original_parameters"],
            "metrics": comparison["metrics"],
            "joint_maximum_ecdf_difference": comparison[
                "joint_maximum_ecdf_difference"
            ],
            "rare_events": comparison["rare_events"],
            "comparison_sha256": hashlib.sha256(comparison_bytes).hexdigest(),
        }
    )
assert len(tests) == 30
ordered = sorted(
    tests, key=lambda row: (row["raw_p"], row["original_row"], row["test"])
)
maximum = 0
for rank, row in enumerate(ordered):
    assert math.isfinite(row["raw_p"]) and 0 <= row["raw_p"] <= 1
    maximum = max(maximum, (30 - rank) * row["raw_p"])
    row["holm_adjusted_p"] = min(1, maximum)
    row["reject_at_familywise_005"] = row["holm_adjusted_p"] <= 0.05
report = {
    "plan_sha256": hashlib.sha256((args.run / "plan.json").read_bytes()).hexdigest(),
    "cohorts": cohorts,
    "original_dispatch_ledger": ledger,
    "recoveries": recovery_records,
    "tests": tests,
    "runs": 1280,
    "observations": 641280,
    "excluded_runs": 0,
    "family_size": 30,
    "familywise_alpha": 0.05,
    "scope": "Outcome-blind ten-setting diagnostic. Holm adjustment covers ten joint six-metric permutation tests and twenty Fisher tests. Inherited per-cohort report prose describes an earlier single-setting experiment; selection provenance and prospective scope come from this frozen plan. No equivalence margin was specified; nonsignificance is not equivalence. These results do not establish historical estimator replication or a whole-paper verdict.",
}
args.output.mkdir()
with (args.output / "tests.csv").open("w") as stream:
    writer = csv.DictWriter(stream, fieldnames=list(tests[0]))
    writer.writeheader()
    writer.writerows(tests)
with (args.output / "cohort-paths.csv").open("w") as stream:
    writer = csv.writer(stream)
    writer.writerow(["original_row", "runs"])
    for index in plan["original_rows_zero_based"]:
        writer.writerow(
            [index, str((cohort_paths[index] / "audit/runs.csv").resolve())]
        )
(args.output / "summary.json").write_text(json.dumps(report, indent=2) + "\n")
print(
    json.dumps(
        {
            "runs": 1280,
            "observations": 641280,
            "rejections": sum(row["reject_at_familywise_005"] for row in tests),
        }
    )
)
