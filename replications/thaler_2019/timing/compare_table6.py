"""Compare complete native Table 6 measurements with the audited paper timings."""

import argparse
import hashlib
import itertools
import json
from pathlib import Path
import re

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("checkpoint", type=Path)
parser.add_argument("audit", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
assets = Path(__file__).resolve().parents[1]
paper_path = assets / "results/archived/paper-timing-comparison.json"
paper = {
    (r["variant"], r["index"]): r
    for r in json.loads(paper_path.read_text())["rows"]
    if r["table"] == 6
}
audit = json.loads((args.audit / "audit.json").read_text())
hashes = json.loads((args.audit / "input-sha256.json").read_text())
for name, digest in hashes.items():
    assert (
        hashlib.sha256((args.checkpoint / "results" / name).read_bytes()).hexdigest()
        == digest
    )
native = {
    (r["condition"]["variant"], r["condition"]["caps"]): r
    for r in audit["rows"]
    if r["condition"]["table"] == 6 and r["accepted"]
}
assert len(native) == len(paper) == 25 and native.keys() == paper.keys()
reports = {}
for name in hashes:
    if name.endswith("/report.html"):
        content = (args.checkpoint / "results" / name).read_bytes()
        reports[hashlib.sha256(content).hexdigest()] = json.loads(
            re.search(r"var reports = (.*);", content.decode())[1]
        )[0]
rows = []
for key in sorted(native, key=lambda k: (k[1], k[0])):
    record = native[key]
    estimate = reports[record["report_sha256"]]["reportAnalysis"]["anRegress"][0][
        "regCoeffs"
    ]["iters"]
    assert abs(estimate["estPoint"] - record["ols_seconds"]) < 1e-9
    error = estimate["estError"]
    assert error["confIntCL"] == 0.05
    # Native Criterion reports can contain a null bootstrap bound. Preserve it.
    bounds = {"lower": error["confIntLDX"], "upper": error["confIntUDX"]}
    interval = {
        bound: {"status": "undefined"}
        if delta is None
        else {"status": "finite", "seconds": estimate["estPoint"] + sign * delta}
        for (bound, delta), sign in zip(bounds.items(), [-1, 1], strict=True)
    }
    rows.append(
        {
            "variant": key[0],
            "capabilities": key[1],
            "paper_seconds": paper[key]["paper_seconds"],
            "native_seconds": record["ols_seconds"],
            "criterion_interval": interval,
            "criterion_raw_error": error,
            "native_speedup_vs_seq": native[("seq", 1)]["ols_seconds"]
            / record["ols_seconds"],
            "paper_speedup_vs_seq": paper[("seq", 1)]["paper_seconds"]
            / paper[key]["paper_seconds"],
        }
    )
pairs = []
for caps in range(1, 9):
    group = [r for r in rows if r["capabilities"] == caps]
    for a, b in itertools.combinations(group, 2):
        overlap = "undefined"
        if all(
            bound["status"] == "finite"
            for r in (a, b)
            for bound in r["criterion_interval"].values()
        ):
            overlap = (
                "yes"
                if max(
                    a["criterion_interval"]["lower"]["seconds"],
                    b["criterion_interval"]["lower"]["seconds"],
                )
                <= min(
                    a["criterion_interval"]["upper"]["seconds"],
                    b["criterion_interval"]["upper"]["seconds"],
                )
                else "no"
            )
        pairs.append(
            {
                "capabilities": caps,
                "a": a["variant"],
                "b": b["variant"],
                "paper_a_faster": a["paper_seconds"] < b["paper_seconds"],
                "native_a_faster": a["native_seconds"] < b["native_seconds"],
                "ranking_matches": (a["paper_seconds"] < b["paper_seconds"])
                == (a["native_seconds"] < b["native_seconds"]),
                "native_intervals_overlap": overlap,
            }
        )
assert len(pairs) == 27
summary = {
    "paper_comparison_sha256": hashlib.sha256(paper_path.read_bytes()).hexdigest(),
    "native_audit_sha256": hashlib.sha256(
        (args.audit / "audit.json").read_bytes()
    ).hexdigest(),
    "conditions": len(rows),
    "pairwise_rankings": len(pairs),
    "matching_rankings": sum(p["ranking_matches"] for p in pairs),
    "rows": rows,
    "pairs": pairs,
    "limits": [
        "Different CPU and topology: descriptive cross-hardware comparison, not an absolute-runtime equivalence test.",
        "Intervals are Criterion's reported slope intervals with confIntCL=0.05; bootstrap intervals were not independently reconstructed.",
        "Four iteration-count measurements per condition are not four independent experiment repetitions.",
        "Interval overlap is descriptive, not a multiple-comparison-adjusted test; speedup ratios have no derived uncertainty intervals.",
        "Table 8, Table 9, retry scaling and concurrent dynamics remain outside this Table 6 comparison.",
    ],
}
with args.output.open("x") as stream:
    stream.write(json.dumps(summary, indent=2) + "\n")
print(
    json.dumps(
        {
            k: summary[k]
            for k in ("conditions", "pairwise_rankings", "matching_rankings")
        }
    )
)
