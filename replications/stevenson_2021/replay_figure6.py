"""Forward-replay the Figure 6(b) recurrence inferred from the vector diagnostic."""

import argparse
import csv
import hashlib
import json
import math
import platform
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("extraction", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
assert not args.output.exists()
audit_bytes = (args.extraction / "audit.json").read_bytes()
audit = json.loads(audit_bytes)
assert (
    audit["pdf_sha256"]
    == "d4e9c64d3792db28af5e0e7e4e2bb67206fcc81f7e94b85ba74d2b05d5aeadaf"
)
assert [curve["rate_label"] for curve in audit["curves"]] == [0.025, 0.47, 2.0, 2.7]
records = []
summaries = []
for curve in audit["curves"]:
    rate = curve["rate_label"]
    path = args.extraction / f"rate-{rate:g}.csv"
    assert hashlib.sha256(path.read_bytes()).hexdigest() == curve["csv_sha256"]
    with path.open() as stream:
        points = list(csv.DictReader(stream))
    assert len(points) == curve["vertices"]
    observed = {
        round(float(row["approximate_cycle"])): float(row["approximate_population"])
        for row in points
        if 1 <= round(float(row["approximate_cycle"])) <= 80
    }
    for expression in ["expanded", "factored", "incremental", "quadratic"]:
        population = 1.0
        capacity = 833.0
        errors = []
        for cycle in range(1, 81):
            assert math.isfinite(population) and population > 0
            # All four expressions are algebraically identical over real numbers.
            # Retain every order; no expression is selected by matching the plot.
            if cycle in observed:
                error = population - observed[cycle]
                errors.append((cycle, error))
                records.append(
                    {
                        "rate": rate,
                        "expression": expression,
                        "cycle": cycle,
                        "predicted_population": population,
                        "vector_population": observed[cycle],
                        "difference": error,
                    }
                )
            if expression == "expanded":
                population = population * (1 + rate - rate * population / capacity)
            elif expression == "factored":
                population = population * (1 + rate * (1 - population / capacity))
            elif expression == "incremental":
                population = population + rate * population * (
                    1 - population / capacity
                )
            else:
                population = (1 + rate) * population - (
                    rate / capacity
                ) * population * population
        windows = {}
        for label, start, stop in [("all", 1, 80), ("early", 1, 40), ("late", 41, 80)]:
            selected = [error for cycle, error in errors if start <= cycle <= stop]
            if not selected:
                windows[label] = {
                    "observed_vertices": 0,
                    "status": "No exported vertices in this window; no interpolation or error estimate",
                }
                continue
            windows[label] = {
                "observed_vertices": len(selected),
                "rms_error": math.sqrt(
                    sum(error * error for error in selected) / len(selected)
                ),
                "max_abs_error": max(abs(error) for error in selected),
            }
        summaries.append({"rate": rate, "expression": expression, "windows": windows})
args.output.mkdir(parents=True, exist_ok=False)
with (args.output / "comparisons.csv").open("x", newline="") as stream:
    writer = csv.DictWriter(stream, fieldnames=list(records[0]))
    writer.writeheader()
    writer.writerows(records)
report = {
    "python": platform.python_version(),
    "initial_population_at_cycle_1": 1,
    "capacity": 833,
    "delay": 0,
    "cycles": 80,
    "extraction_audit_sha256": hashlib.sha256(audit_bytes).hexdigest(),
    "runner_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    "comparisons_sha256": hashlib.sha256(
        (args.output / "comparisons.csv").read_bytes()
    ).hexdigest(),
    "comparisons": len(records),
    "summaries": summaries,
    "scope": "Exploratory reconstruction from plotted curves: initial value 1 and K833 inferred from the prior vector diagnostic, not independently specified paper inputs. Four algebraically equivalent floating-point evaluation orders are retained. No equivalence margin, original-code identity or paper-level verdict.",
}
(args.output / "replay.json").write_text(
    json.dumps(report, indent=2, allow_nan=False) + "\n"
)
print(f"Replayed 16 trajectories and compared {len(records)} exported vertices")
