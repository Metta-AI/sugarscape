"""Reaudit complete trajectories and calculate the fixed-initial-population diagnostic."""

from pathlib import Path
import hashlib
import json
import math
import sys
import tarfile

import numpy as np

workspace, output = map(Path, sys.argv[1:])
assert not output.exists()
results = (
    workspace / "sugarscape-need-for-greed/replications/need_for_greed_2024/results"
)
reports = []
for condition, audit_path, expected_observations in [
    (0.36, results / "selfishness036-metrics-2026-10-19/cohort.json", 490477),
    (0.37, results / "selfishness037-reuse-2026-10-19/audit.json", 495265),
]:
    audit_raw = audit_path.read_bytes()
    audit = json.loads(audit_raw)
    assert audit["native_inputs"] == 100 and audit["condition"] == condition
    groups = {}
    for row in audit["runs"]:
        groups.setdefault(row["native_archive"], {})[
            row["manifest_member"].rsplit("/", 1)[0] + "/trajectory.json"
        ] = row
    records = []
    errors = []
    for archive_name, wanted in sorted(groups.items()):
        archive_path = workspace / "sugarscape-blueprints" / archive_name
        assert (
            hashlib.sha256(archive_path.read_bytes()).hexdigest()
            == audit["native_archive_sha256"][archive_name]
        )
        seen = set()
        with tarfile.open(archive_path, "r|gz") as archive:
            for member in archive:
                if member.name not in wanted:
                    continue
                assert member.name not in seen
                seen.add(member.name)
                expected = wanted[member.name]
                raw = archive.extractfile(member).read()
                assert hashlib.sha256(raw).hexdigest() == expected["trajectory_sha256"]
                rows = json.loads(raw)
                assert (
                    len(rows) == expected["observations"]
                    and rows[0]["population"] == 250
                )
                assert [r["timestep"] for r in rows] == list(range(len(rows)))
                assert rows[-1]["population"] == expected["final_population"]
                assert len(rows) == 5001 or rows[-1]["population"] == 0
                deaths = [
                    r["agentStarvationDeaths"] + r["agentCombatDeaths"] for r in rows
                ]
                assert all(math.isfinite(v) and v >= 0 and int(v) == v for v in deaths)
                matrix = np.array(
                    [
                        [r["agentStarvationDeaths"], r["agentCombatDeaths"]]
                        for r in rows
                    ],
                    dtype=np.float64,
                )
                values = {}
                counts = {}
                for start, suffix in [
                    (0, "including_initial"),
                    (1, "excluding_initial"),
                ]:
                    total = math.fsum(deaths[start:])
                    counts[suffix] = total
                    for mode, steps in [
                        ("observed", len(rows) - start),
                        ("zero_extended", 5001 - start),
                    ]:
                        value = total / steps / 250 * 100
                        independent = float(matrix[start:].sum() / steps * 0.4)
                        error = abs(value - independent) / max(1, abs(value))
                        assert error < 1e-12
                        errors.append(error)
                        values[mode + "/" + suffix] = value
                records.append(
                    {
                        "entry": expected["entry"],
                        "observations": len(rows),
                        "trajectory_sha256": expected["trajectory_sha256"],
                        "death_counts": counts,
                        "values": values,
                    }
                )
        assert seen == wanted.keys()
    assert len(records) == len({r["entry"] for r in records}) == 100
    assert sum(r["observations"] for r in records) == expected_observations
    reports.append(
        {
            "condition": condition,
            "inputs": 100,
            "observations": expected_observations,
            "audit_sha256": hashlib.sha256(audit_raw).hexdigest(),
            "initial_population": 250,
            "runs": sorted(records, key=lambda r: r["entry"]),
            "independent_numpy_values_checked": len(errors),
            "maximum_scaled_error": max(errors),
        }
    )
output.write_text(json.dumps(reports, indent=2) + "\n")
print(
    json.dumps(
        [
            {
                "condition": r["condition"],
                "observations": r["observations"],
                "independent_values": r["independent_numpy_values_checked"],
                "maximum_scaled_error": r["maximum_scaled_error"],
            }
            for r in reports
        ]
    )
)
