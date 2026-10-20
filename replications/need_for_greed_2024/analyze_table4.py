"""Analyze Table IV rows only after their complete original input sets are audited."""

import argparse
from collections import Counter
from decimal import Decimal
import gzip
import hashlib
import json
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter

INPUTS_SHA256 = "368c43d13e42bcddc867dfa12acbd57ce73a47d2b333c5978599083410a85b8f"


class OriginalInput(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    condition: str
    disposition: str
    entry: str
    kind: Literal["baseline", "sweep"]
    original_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    seed: int = Field(ge=0)


class AuditedRun(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    entry: str
    observations: int = Field(ge=1, le=5001)
    trajectory_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    final_population: int = Field(ge=0, le=2500)


class OutcomeCounts(BaseModel):
    extinct: int
    worse: int
    better: int


class TableRow(BaseModel):
    label: str
    required_inputs: int
    audited_inputs: int
    missing_entries: list[str]
    complete: bool
    paper_counts: OutcomeCounts
    released_plot_counts: OutcomeCounts
    equal_initial_population: int
    published_percentages: list[float]
    published_percentage_sum: float
    complete_percentages: list[float]
    complete_percentage_point_differences: list[float]


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
    source_path = Path(__file__).with_name("source-audit.json")
    source_raw = source_path.read_bytes()
    targets = json.loads(source_raw)["targets"]["table_IV"]["rows"]
    covered = set()
    reports = []
    for label, *published in targets:
        edges = label.split("-")
        low, high = Decimal(edges[0]), Decimal(edges[-1])
        expected = {
            row.entry
            for row in originals
            if row.kind == "sweep" and low <= Decimal(row.condition) <= high
        }
        assert expected and not covered.intersection(expected)
        covered.update(expected)
        assert len(expected) == (int((high - low) * 100) + 1) * 100
        assert all(
            count == 100
            for count in Counter(lookup[e].condition for e in expected).values()
        )
        selected = [audited[e] for e in sorted(expected & audited.keys())]
        counts = OutcomeCounts(extinct=0, worse=0, better=0)
        equal = 0
        for run in selected:
            if run.final_population == 0:
                counts.extinct += 1
            elif run.final_population <= 250:
                counts.worse += 1
                equal += run.final_population == 250
            else:
                counts.better += 1
        missing = sorted(expected - audited.keys())
        percentages = []
        differences = []
        if not missing:
            percentages = [
                100 * n / len(expected)
                for n in (counts.extinct, counts.worse, counts.better)
            ]
            differences = [
                float(Decimal(str(a)) - Decimal(str(b)))
                for a, b in zip(percentages, published, strict=True)
            ]
        reports.append(
            TableRow(
                label=label,
                required_inputs=len(expected),
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
                published_percentages=published,
                published_percentage_sum=float(sum(Decimal(str(x)) for x in published)),
                complete_percentages=percentages,
                complete_percentage_point_differences=differences,
            )
        )
    assert covered == {r.entry for r in originals if r.kind == "sweep"}
    assert len(covered) == 10100
    report = {
        "inventory_sha256": hashlib.sha256(inventory_raw).hexdigest(),
        "original_inputs_sha256": INPUTS_SHA256,
        "source_audit_sha256": hashlib.sha256(source_raw).hexdigest(),
        "required_sweep_inputs": len(covered),
        "audited_sweep_inputs": len(covered & audited.keys()),
        "complete_rows": sum(r.complete for r in reports),
        "rows": [r.model_dump() for r in reports],
        "scope": "Audited inventory aggregation, not a new raw-trajectory audit. No percentages or comparisons for incomplete rows. Exact percentage-point differences are descriptive; no rounding rule, significance, or paper-completion verdict is inferred.",
    }
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: v for k, v in report.items() if k != "rows"}))


if __name__ == "__main__":
    main()
