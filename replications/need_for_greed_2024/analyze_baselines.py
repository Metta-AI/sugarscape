"""Compare Tables I–III only when all original baseline inputs are audited."""

import argparse
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path

from pydantic import BaseModel, TypeAdapter

from analyze_table4 import (
    INPUTS_SHA256,
    AuditedRun,
    OriginalInput,
    OutcomeCounts,
    TableRow,
)


class BaselineTarget(BaseModel):
    table: str
    condition: str
    source_text: str
    percentages: list[float]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("original_inputs", type=Path)
    parser.add_argument("inventory", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    assert not args.output.exists()
    raw_inputs = args.original_inputs.read_bytes()
    assert hashlib.sha256(raw_inputs).hexdigest() == INPUTS_SHA256
    originals = TypeAdapter(list[OriginalInput]).validate_json(
        gzip.decompress(raw_inputs)
    )
    lookup = {row.entry: row for row in originals}
    assert len(lookup) == len(originals) == 10500
    inventory_raw = args.inventory.read_bytes()
    inventory = json.loads(inventory_raw)
    runs = TypeAdapter(list[AuditedRun]).validate_python(inventory["runs"])
    audited = {row.entry: row for row in runs}
    assert len(audited) == len(runs) == inventory["audited_inputs"]
    assert sum(r.observations for r in runs) == inventory["audited_observations"]
    assert audited.keys() <= lookup.keys()
    source_raw = Path(__file__).with_name("source-audit.json").read_bytes()
    source = json.loads(source_raw)["targets"]
    targets = [
        BaselineTarget(
            table="table_I",
            condition="altruisticHalfLookaheadBinary",
            source_text="Selfishness 0: extinct 67%, worse 2%, better 31%.",
            percentages=[67, 2, 31],
        ),
        BaselineTarget(
            table="table_II",
            condition="egoisticHalfLookaheadBinary",
            source_text="Selfishness 1: extinct 62%, worse 2%, better 36%.",
            percentages=[62, 2, 36],
        ),
        BaselineTarget(
            table="table_III",
            condition="benthamHalfLookaheadBinary",
            source_text="Selfishness 0.5: extinct 0%, worse 0%, better 100%.",
            percentages=[0, 0, 100],
        ),
    ]
    baseline_counts = Counter(
        row.condition for row in originals if row.kind == "baseline"
    )
    assert baseline_counts == {t.condition: 100 for t in targets} | {
        "rawSugarscape": 100
    }
    reports = []
    covered = set()
    for target in targets:
        assert source[target.table] == target.source_text
        expected = {
            row.entry
            for row in originals
            if row.kind == "baseline" and row.condition == target.condition
        }
        assert len(expected) == 100 and not covered.intersection(expected)
        covered.update(expected)
        selected = [audited[e] for e in sorted(expected & audited.keys())]
        counts = OutcomeCounts(extinct=0, worse=0, better=0)
        equal = 0
        for row in selected:
            if row.final_population == 0:
                counts.extinct += 1
            elif row.final_population <= 250:
                counts.worse += 1
                equal += row.final_population == 250
            else:
                counts.better += 1
        missing = sorted(expected - audited.keys())
        percentages = []
        differences = []
        if not missing:
            percentages = [
                float(n) for n in (counts.extinct, counts.worse, counts.better)
            ]
            differences = [
                a - b for a, b in zip(percentages, target.percentages, strict=True)
            ]
        reports.append(
            TableRow(
                label=target.table,
                required_inputs=100,
                audited_inputs=len(selected),
                missing_entries=missing,
                complete=not missing,
                paper_counts=counts,
                released_plot_counts=OutcomeCounts(
                    extinct=counts.extinct,
                    worse=counts.worse - equal,
                    better=counts.better + equal,
                ),
                equal_initial_population=equal,
                published_percentages=target.percentages,
                published_percentage_sum=sum(target.percentages),
                complete_percentages=percentages,
                complete_percentage_point_differences=differences,
            )
        )
    report = {
        "inventory_sha256": hashlib.sha256(inventory_raw).hexdigest(),
        "original_inputs_sha256": INPUTS_SHA256,
        "source_audit_sha256": hashlib.sha256(source_raw).hexdigest(),
        "required_table_inputs": len(covered),
        "audited_table_inputs": len(covered & audited.keys()),
        "raw_control_audited_inputs": sum(
            lookup[r.entry].kind == "baseline"
            and lookup[r.entry].condition == "rawSugarscape"
            for r in runs
        ),
        "complete_rows": sum(r.complete for r in reports),
        "rows": [r.model_dump() for r in reports],
        "scope": "Audited baseline inventory only; no sweep endpoint substitution. Percentages withheld until all 100 original inputs are present. Descriptive differences do not constitute a paper-completion verdict or a new trajectory audit.",
    }
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: v for k, v in report.items() if k != "rows"}))


if __name__ == "__main__":
    main()
