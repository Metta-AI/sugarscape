"""Audit complete paired trajectories and exact source substitutions."""

import argparse
import csv
import hashlib
import json
from pathlib import Path
import numpy as np
from scipy import stats

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("root", type=Path)
parser.add_argument("baseline", type=Path)
parser.add_argument("protocol", type=Path)
parser.add_argument("--output", type=Path, required=True)
args = parser.parse_args()
root = args.root
baseline = args.baseline
protocol = json.loads(args.protocol.read_text())
assert json.loads((root / "complete.json").read_text()) == {"completed_variants": 3}
report = {
    "protocol_sha256": hashlib.sha256(args.protocol.read_bytes()).hexdigest(),
    "scope": "Single-seed source diagnosis; no paper-level or statistical replication verdict",
    "variants": [],
}
for variant, patch_names in protocol["variants"].items():
    folder = root / variant
    assert json.loads((folder / "complete.json").read_text()) == {
        "completed_trajectories": 3
    }
    manifest = json.loads((folder / "manifest.json").read_text())
    changed = []
    for name, digest in protocol["baseline_source_sha256"].items():
        original = (baseline / "source" / name).read_bytes()
        assert hashlib.sha256(original).hexdigest() == digest, name
        expected = original
        for patch_name in patch_names:
            patch = protocol["patches"][patch_name]
            if patch["path"] == name:
                before, after = patch["before"].encode(), patch["after"].encode()
                assert expected.count(before) == 1
                expected = expected.replace(before, after)
        actual = (folder / "source" / name).read_bytes()
        assert actual == expected, (variant, name)
        assert hashlib.sha256(actual).hexdigest() == manifest["source_sha256"][name]
        if actual != original:
            changed.append(name)
    assert (folder / "Observe.hs").read_bytes() == (
        baseline / "Observe.hs"
    ).read_bytes()
    result = {
        "variant": variant,
        "changed_source_files": changed,
        "binary_sha256": hashlib.sha256((folder / "observe").read_bytes()).hexdigest(),
        "cases": [],
    }
    for case, constructor, horizon in protocol["scenarios"]:
        summaries = list(csv.DictReader((folder / f"{case}.summary.csv").open()))
        old = list(csv.DictReader((baseline / f"{case}.summary.csv").open()))
        assert [int(r["time"]) for r in summaries] == list(range(horizon + 1))
        assert len(old) == len(summaries)
        differences = {
            field: sum(a[field] != b[field] for a, b in zip(summaries, old))
            for field in summaries[0]
        }
        if variant == "observation":
            for field in [
                "time",
                "population",
                "environment_sugar",
                "environment_spice",
                "pollution",
            ]:
                assert differences[field] == 0, (
                    variant,
                    case,
                    field,
                    differences[field],
                )
        agents = list(csv.DictReader((folder / f"{case}.agents.csv").open()))
        by_time = {t: [] for t in range(horizon + 1)}
        for row in agents:
            by_time[int(row["time"])].append(row)
        for row in summaries:
            t = int(row["time"])
            assert len(by_time[t]) == int(row["population"])
            assert len({int(a["id"]) for a in by_time[t]}) == len(by_time[t])
            assert np.isfinite([float(row[k]) for k in row]).all()
        cells = list(csv.DictReader((folder / f"{case}.cells.csv").open()))
        spatial = []
        for t in [0, horizon]:
            sites = [r for r in cells if int(r["time"]) == t]
            coords = {(int(r["x"]), int(r["y"])) for r in sites}
            assert len(coords) == len(sites)
            if variant in ["index", "both"]:
                assert coords == {(x, y) for y in range(51) for x in range(51)}, (
                    variant,
                    case,
                    t,
                    "grid",
                )
            owners = {
                int(r["occupier"]): (int(r["x"]), int(r["y"]))
                for r in sites
                if int(r["occupier"]) >= 0
            }
            positions = {int(r["id"]): (int(r["x"]), int(r["y"])) for r in by_time[t]}
            spatial.append(
                {
                    "time": t,
                    "cells": len(sites),
                    "agents": len(positions),
                    "occupiers": len(owners),
                    "missing_occupier_ids": sorted(set(positions) - set(owners)),
                    "coordinate_disagreements": sum(
                        owners.get(k) != v for k, v in positions.items()
                    ),
                }
            )
        final = np.array([float(a["sugar"]) for a in by_time[horizon]])
        assert np.isfinite(final).all() and len(final) > 1 and final.sum() > 0
        sorted_wealth = np.sort(final)
        n = len(final)
        gini = float(
            2 * np.sum(np.arange(1, n + 1) * sorted_wealth) / (n * final.sum())
            - (n + 1) / n
        )
        pairwise = float(
            np.abs(final[:, None] - final[None, :]).sum() / (2 * n * final.sum())
        )
        assert abs(gini - pairwise) < 1e-12
        trades = [
            r
            for r in csv.DictReader((folder / f"{case}.trades.csv").open())
            if int(r["time"]) == horizon
        ]
        prices = np.array([float(r["price"]) for r in trades])
        measures = {
            "final_population": n,
            "final_sugar_gini": gini,
            "final_sugar_skewness": float(stats.skew(final, bias=True)),
            "final_sugar_excess_kurtosis": float(
                stats.kurtosis(final, fisher=True, bias=True)
            ),
            "mean_population_last300": float(
                np.mean([int(r["population"]) for r in summaries[101:]])
            )
            if case == "carrying"
            else None,
            "final_trade_observations": len(prices),
            "final_price_sample_sd": float(prices.std(ddof=1))
            if len(prices) > 1
            else None,
        }
        result["cases"].append(
            {
                "scenario": case,
                "horizon": horizon,
                "agent_observations": len(agents) - len(by_time[0]),
                "summary_field_differing_timesteps": differences,
                "spatial": spatial,
                "measurements": measures,
                "files_sha256": {
                    p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                    for p in sorted(folder.glob(case + ".*"))
                },
            }
        )
    report["variants"].append(result)
output = args.output
assert not output.exists()
output.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
print(
    json.dumps(
        {
            "variants": len(report["variants"]),
            "cases": sum(len(v["cases"]) for v in report["variants"]),
            "scope": report["scope"],
        }
    )
)
