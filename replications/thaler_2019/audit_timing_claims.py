"""Compare explicit timing propositions with published cells and audited native fits."""

import argparse
import hashlib
import json
from pathlib import Path
import subprocess

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("paper", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
base = Path(__file__).resolve().parent
comparison_path = base / "results/timing-grid-complete-2026-10-18/comparison.json"
comparison = json.loads(comparison_path.read_bytes())
assert comparison["conditions"] == 51
target_path = base / "results/archived/paper-timing-comparison.json"
assert (
    hashlib.sha256(target_path.read_bytes()).hexdigest() == comparison["target_sha256"]
)
for name, digest in comparison["input_audit_sha256"].items():
    assert hashlib.sha256((base.parents[1] / name).read_bytes()).hexdigest() == digest
archive = json.loads((base / "results/archived/archived-ols-audit.json").read_bytes())
assert hashlib.sha256(args.paper.read_bytes()).hexdigest() == archive["paper_sha256"]
text = subprocess.check_output(
    ["pdftotext", "-layout", str(args.paper), "-"], text=True
)
pages = text.split("\f")
assert "sweet spot" in pages[19] and "at 3 cores" in pages[20]
assert "Lock-Based performs better than the TVar" in pages[22]
rows = comparison["rows"]
assert len({(r["table"], r["variant"], r["index"]) for r in rows}) == 51
claims = []
for field in ["paper_seconds", "native_seconds"]:
    data = {(r["table"], r["variant"], r["index"]): r[field] for r in rows}
    findings = []
    for variant in ["io", "tvar"]:
        values = {n: data[6, variant, n] for n in range(1, 9)}
        findings.append(
            {
                "claim": f"table6_{variant}_optimum_at_three",
                "paper_page": 21,
                "condition_seconds": values,
                "minimum_at": min(values, key=values.__getitem__),
                "holds_for_point_estimates": values[3] == min(values.values()),
            }
        )
    for table, indices, first, second in [
        (6, range(1, 9), "io", "tvar"),
        (8, range(500, 2501, 500), "io", "tvar"),
    ]:
        comparisons = [
            {
                "index": n,
                "first_seconds": data[table, first, n],
                "second_seconds": data[table, second, n],
                "holds": data[table, first, n] < data[table, second, n],
            }
            for n in indices
        ]
        findings.append(
            {
                "claim": f"table{table}_lock_faster_than_tvar_every_condition",
                "paper_page": 20 if table == 6 else 23,
                "comparisons": comparisons,
                "holds_for_point_estimates": all(r["holds"] for r in comparisons),
            }
        )
    for table, indices in [(6, range(3, 9)), (8, range(500, 2501, 500))]:
        comparisons = []
        for n in indices:
            values = {
                variant: data[
                    table, variant, 1 if table == 6 and variant == "seq" else n
                ]
                for variant in ["io", "seq", "tvar", "tarray"]
            }
            comparisons.append(
                {
                    "index": n,
                    "seconds": values,
                    "holds": values["tarray"] == min(values.values()),
                }
            )
        findings.append(
            {
                "claim": f"table{table}_tarray_fastest_selected_conditions",
                "paper_page": 20 if table == 6 else 23,
                "comparisons": comparisons,
                "holds_for_point_estimates": all(r["holds"] for r in comparisons),
            }
        )
    values = {
        variant: data[6, variant, 1] for variant in ["io", "seq", "tvar", "tarray"]
    }
    findings.append(
        {
            "claim": "table6_tarray_slowest_at_one",
            "paper_page": 21,
            "seconds": values,
            "holds_for_point_estimates": values["tarray"] == max(values.values()),
        }
    )
    for variant, first, second in [
        ("seq", 2500, 2000),
        ("tvar", 2500, 2000),
        ("seq", 2000, 1500),
        ("io", 2000, 1500),
    ]:
        findings.append(
            {
                "claim": f"table8_{variant}_{first}_faster_than_{second}",
                "paper_page": 23,
                "first_seconds": data[8, variant, first],
                "second_seconds": data[8, variant, second],
                "holds_for_point_estimates": data[8, variant, first]
                < data[8, variant, second],
            }
        )
    for variant in ["normal", "rebirthing"]:
        values = [data[9, variant, n] for n in [16, 32, 64]]
        findings.append(
            {
                "claim": f"table9_{variant}_slower_with_more_capabilities",
                "paper_page": 23,
                "seconds_at_16_32_64": values,
                "holds_for_point_estimates": values[0] < values[1] < values[2],
            }
        )
    claims.append({"measurement": field, "claims": findings})
report = {
    "paper_sha256": hashlib.sha256(args.paper.read_bytes()).hexdigest(),
    "comparison_sha256": hashlib.sha256(comparison_path.read_bytes()).hexdigest(),
    "results": claims,
    "scope": "Post-hoc descriptive proposition audit. No significance, timing equivalence, causal explanation, or completed-study verdict. Paper prose and paper tables are separate targets. Native Tables 6/8 use different hardware; Table 9 matches instance class without historical scheduling evidence.",
}
args.output.mkdir(parents=True, exist_ok=False)
(args.output / "claims.json").write_text(json.dumps(report, indent=2) + "\n")
print(
    json.dumps(
        {
            r["measurement"]: [
                c["claim"] for c in r["claims"] if not c["holds_for_point_estimates"]
            ]
            for r in claims
        }
    )
)
