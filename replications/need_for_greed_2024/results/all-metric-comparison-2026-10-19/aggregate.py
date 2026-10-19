"""Audit retained native trajectories and aggregate all five paper measurements."""

from pathlib import Path
from statistics import median
import hashlib
import json
import math
import sys
import tarfile

repo, audit_path, output = map(Path, sys.argv[1:])
assert not output.exists()
audit_raw = audit_path.read_bytes()
audit = json.loads(audit_raw)
assert audit["native_inputs"] == 100 and audit["condition"] == 0.37
groups = {}
for row in audit["runs"]:
    groups.setdefault(row["native_archive"], {})[
        row["manifest_member"].rsplit("/", 1)[0] + "/trajectory.json"
    ] = row
rows = []
for path, wanted in sorted(groups.items()):
    assert (
        hashlib.sha256((repo / path).read_bytes()).hexdigest()
        == audit["native_archive_sha256"][path]
    )
    seen = set()
    with tarfile.open(repo / path, mode="r|gz") as archive:
        for member in archive:
            if member.name not in wanted:
                continue
            assert member.name not in seen
            seen.add(member.name)
            expected = wanted[member.name]
            raw = archive.extractfile(member).read()
            assert hashlib.sha256(raw).hexdigest() == expected["trajectory_sha256"]
            records = json.loads(raw)
            assert len(records) == expected["observations"]
            assert [r["timestep"] for r in records] == list(range(len(records)))
            assert records[-1]["population"] == expected["final_population"]
            assert len(records) == 5001 or records[-1]["population"] == 0
            values = {}
            diagnostics = {}
            for exclude_initial in [False, True]:
                selected = records[int(exclude_initial) :]
                suffix = "excluding_initial" if exclude_initial else "including_initial"
                positive = [r for r in selected if r["population"] > 0]
                deaths = [
                    r["agentStarvationDeaths"] + r["agentCombatDeaths"]
                    for r in selected
                ]
                assert all(math.isfinite(v) and v >= 0 for v in deaths)
                rates = [
                    (r["agentStarvationDeaths"] + r["agentCombatDeaths"])
                    * 100
                    / r["population"]
                    for r in positive
                ]
                diagnostics[suffix] = {
                    "observations": len(selected),
                    "positive_population_rows": len(positive),
                    "zero_population_rows": len(selected) - len(positive),
                    "deaths_at_zero_population": sum(
                        r["agentStarvationDeaths"] + r["agentCombatDeaths"]
                        for r in selected
                        if r["population"] == 0
                    ),
                    "future_zero_rows": 5001 - len(records),
                }
                for metric in [
                    "population",
                    "meanWealth",
                    "agentMeanTimeToLive",
                    "meanAgeAtDeath",
                ]:
                    assert all(math.isfinite(r[metric]) for r in selected)
                    total = math.fsum(r[metric] for r in selected)
                    values[metric + "/observed/" + suffix] = total / len(selected)
                    values[metric + "/zero_extended/" + suffix] = total / (
                        5001 - int(exclude_initial)
                    )
                values["death_percent/positive_rows/" + suffix] = math.fsum(
                    rates
                ) / len(positive)
                values["death_percent/zero_rows_set_zero/" + suffix] = math.fsum(
                    rates
                ) / len(selected)
                values["death_percent/zero_extended/" + suffix] = math.fsum(rates) / (
                    5001 - int(exclude_initial)
                )
                values["death_percent/ratio_of_sums/" + suffix] = (
                    math.fsum(deaths)
                    * 100
                    / math.fsum(r["population"] for r in selected)
                )
            rows.append(
                {
                    "entry": expected["entry"],
                    "seed": expected["seed"],
                    "trajectory_sha256": expected["trajectory_sha256"],
                    "observations": len(records),
                    "values": values,
                    "diagnostics": diagnostics,
                }
            )
    assert seen == wanted.keys()
rows.sort(key=lambda r: r["entry"])
assert len(rows) == len({r["entry"] for r in rows}) == 100
medians = {key: median(row["values"][key] for row in rows) for key in rows[0]["values"]}
report = {
    "cohort_audit_sha256": hashlib.sha256(audit_raw).hexdigest(),
    "inputs": 100,
    "observations": sum(r["observations"] for r in rows),
    "medians": medians,
    "runs": rows,
    "scope": "Per-run means followed by across-seed medians. Four conventions per direct metric and eight starvation-plus-combat death-rate conventions. Disease and aging deaths excluded per paper. Zero extension is an explicit post-extinction assumption. No author aggregation identification or completed-paper claim.",
}
output.write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(medians, indent=2))
