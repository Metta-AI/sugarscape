"""Compare all twenty printed Table 1 means with complete declared reconstructions."""

import argparse
import csv
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import re

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("paper_tex", type=Path)
parser.add_argument("evolution_analysis", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
assert (
    hashlib.sha256(args.paper_tex.read_bytes()).hexdigest()
    == "081d7e5c265dd72f3d631000cbdd8e826057e8b5c91bb366e8f988f1797f459a"
)
source = args.paper_tex.read_text()
targets = {}
excerpts = []
for scenario, label in [
    ("low-fertility", "Low Fertility"),
    ("birth-cost", "Birth Cost"),
    ("stable", "Evolved Stable"),
    ("chaotic", "Evolved Chaos"),
]:
    matches = [
        line.strip()
        for line in source.splitlines()
        if line.strip().startswith(label + " &")
    ]
    assert len(matches) == 1
    excerpts.extend(matches)
    cells = matches[0].split("&")
    assert len(cells) == 8
    targets[scenario] = {
        "infertility": int(cells[1]),
        "birth_cost": int(cells[2]),
        "metrics": {},
    }
    for metric, cell in zip(
        ["growth_rate", "population", "mean_age", "wealth", "gini"],
        cells[3:],
        strict=True,
    ):
        found = re.findall(r"\$(\d+(?:\.\d+)?)\\pm(\d+(?:\.\d+)?)\\%\$", cell)
        assert len(found) == 1
        mean, percentage = found[0]
        targets[scenario]["metrics"][metric] = {
            "printed_mean": mean,
            "printed_plus_minus_percent": percentage,
        }
results = Path(__file__).parent / "results"
paths = {
    "fixed-low-fertility": results / "low-fertility-ensemble-2026-10-15/analysis.json",
    "fixed-birth-cost": results / "birth-cost-ensemble-2026-10-15/analysis.json",
    "fixed-growth": results / "growth-2026-10-15/analysis.json",
    "selected-growth": results / "selected-growth-2026-10-18/analysis/analysis.json",
    "evolution": args.evolution_analysis / "analysis.json",
}
inputs = {name: json.loads(path.read_text()) for name, path in paths.items()}
evolution = inputs["evolution"]
assert evolution["validated_runs"] == 200 and evolution["mode"] == "complete-ensemble"
assert [(r["scenario"], r["seed"]) for r in evolution["per_seed"]] == [
    (s, i) for i in range(100) for s in ["stable", "chaotic"]
]
rows = []
for scenario in targets:
    if scenario in ["low-fertility", "birth-cost"]:
        steady = inputs["fixed-" + scenario]
        assert steady["validated_runs"] == 100 and not steady["extinct_seeds"]
        estimates = steady["statistics"]
        growth = inputs["fixed-growth"]["summaries"][scenario]
    else:
        steady = evolution["statistics"][scenario]
        assert not steady["extinct_seeds"], "No survivor-only Table 1 summary"
        estimates = steady["estimates"]
        growth = inputs["selected-growth"]["summaries"]["selected-" + scenario]
    assert growth["requested"] == growth["fitted"] == 100
    for metric, target in targets[scenario]["metrics"].items():
        measured = (
            growth["r"] if metric == "growth_rate" else estimates[metric]["later"]
        )
        printed = Decimal(target["printed_mean"])
        value = measured["mean"]
        rows.append(
            {
                "scenario": scenario,
                "metric": metric,
                **target,
                "reconstruction_mean": value,
                "seed_sd": measured["sd"],
                "seed_mean_ci95_low": measured["ci95"][0],
                "seed_mean_ci95_high": measured["ci95"][1],
                "difference": value - float(printed),
                "relative_difference_percent": 100 * (value / float(printed) - 1),
                "same_rounded_mean": Decimal(str(value)).quantize(printed) == printed,
                "measurement": "one-founder continuous logistic fit"
                if metric == "growth_rate"
                else "seed-averaged cycle samples 75100..100000 every100",
            }
        )
assert len(rows) == 20
args.output.mkdir(parents=True, exist_ok=False)
with (args.output / "comparison.csv").open("w") as stream:
    writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)
(args.output / "table1-source-rows.tex").write_text("\n".join(excerpts) + "\n")
(args.output / "targets.json").write_text(json.dumps(targets, indent=2) + "\n")
(args.output / "audit.json").write_text(
    json.dumps(
        {
            "paper": "https://arxiv.org/abs/2108.11892v2",
            "paper_tex_sha256": hashlib.sha256(args.paper_tex.read_bytes()).hexdigest(),
            "inputs_sha256": {
                str(path): hashlib.sha256(path.read_bytes()).hexdigest()
                for path in paths.values()
            },
            "comparison_rows": len(rows),
            "interpretation": "Descriptive comparison only. Printed percentage meanings, original windows and growth-fitting convention remain unresolved. Population is mapped to printed K via late-window mean, not fitted logistic K. Matching rounded values is not equivalence, and our confidence intervals do not interpret paper percentages.",
        },
        indent=2,
    )
    + "\n"
)
print(json.dumps(rows))
