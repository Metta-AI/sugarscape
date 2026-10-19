"""Verify the native disease-count correction and unchanged 10-disease controls."""

import argparse
import ast
import csv
import hashlib
import json
import math
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("root", type=Path)
parser.add_argument("native_home", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
protocol = json.loads((args.root / "protocol.json").read_text())
assert json.loads((args.root / "complete.json").read_text()) == {"completed_runs": 4}
results = []
for variant, spec in protocol["variants"].items():
    root = args.root / variant
    baseline = args.native_home / Path(spec["baseline"]["root"]).relative_to(
        "/root/sugarscape"
    )
    changed = []
    for name, digest in spec["baseline"]["source_sha256"].items():
        before = (baseline / "source" / name).read_bytes()
        after = (root / "source" / name).read_bytes()
        assert hashlib.sha256(before).hexdigest() == digest
        assert hashlib.sha256(after).hexdigest() == spec["source_sha256"][name]
        if before != after:
            changed.append(name)
    assert changed == ["src/SugarScape/Core/Init.hs"]
    before = (baseline / "source" / changed[0]).read_bytes()
    assert before.count(b"Just (isl, dl, dc, ad, _)") == 1
    assert before.count(b"Just (isl, dl, dc, ad, ml)") == 1
    expected = before.replace(
        b"Just (isl, dl, dc, ad, _)", b"Just (isl, dc, dl, ad, _)"
    ).replace(b"Just (isl, dl, dc, ad, ml)", b"Just (isl, dc, dl, ad, ml)")
    assert (root / "source" / changed[0]).read_bytes() == expected
    assert (root / "Observe.hs").read_bytes() == (baseline / "Observe.hs").read_bytes()
    assert (
        hashlib.sha256((root / "Observe.hs").read_bytes()).hexdigest()
        == spec["observer_sha256"]
    )
    assert (
        hashlib.sha256((baseline / "observe").read_bytes()).hexdigest()
        == spec["baseline"]["binary_sha256"]
    )
    for label, constructor, steps, stride in protocol["first_cases"]:
        prefix = root / "first" / label
        assert not Path(str(prefix) + ".stderr.log").read_bytes()
        assert not Path(str(prefix) + ".stdout.log").read_bytes()
        text = Path(str(prefix) + ".scenario.txt").read_text()
        assert text.startswith(
            f"Constructor: {constructor}\nSeed: {protocol['seed']}\n"
        )
        declaration = next(
            line
            for line in text.splitlines()
            if line.startswith("E rule active (disease):")
        )
        immune, count, maximum_length, initial, pool = ast.literal_eval(
            declaration.split("Just ", 1)[1]
        )
        assert immune == 50 and maximum_length == 10
        assert count == len(pool) == (10 if label == "disease_clear" else 25)
        assert initial == (4 if label == "disease_clear" else 10)
        assert all(1 <= len(disease) <= maximum_length for disease in pool)
        assert all(type(bit) is bool for disease in pool for bit in disease)
        if label == "disease_clear":
            prior = (
                args.native_home
                / "thaler-properties-observer-ensembles-001"
                / spec["baseline_variant"]
                / label
                / f"000-{protocol['seed']}"
            )
            for suffix in [
                "summary.csv",
                "agents.csv",
                "cells.csv",
                "trades.csv",
                "scenario.txt",
            ]:
                assert (
                    Path(str(prefix) + "." + suffix).read_bytes()
                    == (prior / ("trajectory." + suffix)).read_bytes()
                ), (variant, suffix)
        summaries = list(csv.DictReader(Path(str(prefix) + ".summary.csv").open()))
        assert [int(row["time"]) for row in summaries] == list(range(steps + 1))
        assert all(
            math.isfinite(float(value)) for row in summaries for value in row.values()
        )
        assert all(
            0 <= int(row["infected"]) <= int(row["population"]) for row in summaries
        )
        frames = {t: {} for t in range(0, steps + 1, stride)}
        for row in csv.DictReader(Path(str(prefix) + ".agents.csv").open()):
            t, aid = int(row["time"]), int(row["id"])
            assert t in frames and aid not in frames[t]
            assert row["culture"] == ""
            assert all(
                math.isfinite(float(v)) for k, v in row.items() if k != "culture"
            )
            assert int(row["disease_count"]) >= 0
            frames[t][aid] = row
        for t, members in frames.items():
            assert len(members) == int(summaries[t]["population"])
            assert sum(
                int(row["disease_count"]) > 0 for row in members.values()
            ) == int(summaries[t]["infected"])
            for resource in ["sugar", "spice"]:
                assert math.isclose(
                    sum(float(row[resource]) for row in members.values()),
                    float(summaries[t]["agent_" + resource]),
                    rel_tol=1e-12,
                    abs_tol=1e-8,
                )
        cells = {0: {}, steps: {}}
        for row in csv.DictReader(Path(str(prefix) + ".cells.csv").open()):
            t = int(row["time"])
            coord = int(row["x"]), int(row["y"])
            assert t in cells and coord not in cells[t]
            assert all(math.isfinite(float(v)) for v in row.values())
            cells[t][coord] = row
        for t, sites in cells.items():
            assert len(sites) == (
                2551 if variant == "disease_count_corrected" else 2601
            )
            for resource in ["sugar", "spice"]:
                assert math.isclose(
                    sum(float(row[resource]) for row in sites.values()),
                    float(summaries[t]["environment_" + resource]),
                    rel_tol=1e-12,
                    abs_tol=1e-8,
                )
        assert not list(csv.DictReader(Path(str(prefix) + ".trades.csv").open()))
        last = summaries[-1]
        results.append(
            {
                "variant": variant,
                "case": label,
                "seed": protocol["seed"],
                "steps": steps,
                "source_files_verified": len(spec["source_sha256"]),
                "binary_sha256": hashlib.sha256(
                    (root / "observe").read_bytes()
                ).hexdigest(),
                "generated_diseases": count,
                "distinct_diseases": len(set(map(tuple, pool))),
                "disease_lengths": list(map(len, pool)),
                "unchanged_baseline_control": label == "disease_clear",
                "agent_observations": sum(map(len, frames.values())),
                "final_population": int(last["population"]),
                "final_infected": int(last["infected"]),
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
                "prose_infected_majority": 2 * int(last["infected"])
                > int(last["population"]),
                "files_sha256": {
                    p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                    for p in sorted((root / "first").glob(label + ".*"))
                },
            }
        )
report = {
    "protocol_sha256": hashlib.sha256(
        (args.root / "protocol.json").read_bytes()
    ).hexdigest(),
    "auditor_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    "results": results,
    "scope": "Two unchanged complete native controls and two intended-configuration trajectories. First-seed evidence only; no ensemble or whole-paper verdict.",
}
with args.output.open("x") as stream:
    stream.write(json.dumps(report, indent=2, allow_nan=False) + "\n")
print(
    json.dumps(
        [
            {k: v for k, v in r.items() if k not in ["files_sha256", "disease_lengths"]}
            for r in results
        ]
    )
)
