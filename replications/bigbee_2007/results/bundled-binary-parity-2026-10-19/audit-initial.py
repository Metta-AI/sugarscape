"""Compare original bytecode replays to the existing historical source rebuild."""

from pathlib import Path
import csv
import gzip
import hashlib
import json
import re
import sys

root, old, output = map(Path, sys.argv[1:])
assert not output.exists()
manifest = json.loads((root / "manifest.json").read_text())
engine = root / "native/mason_sugarscape_1.1"
expected_origin = engine.as_uri() + "/"
receipts = json.loads((root / "runs.json").read_text())
assert len(receipts) == 9 and all(r["exit_code"] == 0 for r in receipts)
reports = []
for config in ["anim2-3", "fig3-4", "fig3-5"]:
    current = (root / (config + "-a.stdout")).read_bytes()
    reference = gzip.decompress((old / (config + "-a.stdout.gz")).read_bytes())
    assert current == reference
    provenance = []
    for repeat in ["a", "b", "observer"]:
        stem = config + "-" + repeat
        assert (root / (stem + ".stdout")).read_bytes() == current
        assert (root / (stem + ".stderr")).read_bytes() == b""
        source = (root / (stem + ".classes.log")).read_text()
        loaded = re.findall(
            r"\[class,load\] (sim\.app\.sugarscape\.\S+|sim\.engine\.\S+|ec\.util\.MersenneTwisterFast) source: (\S+)",
            source,
        )
        assert loaded and all(origin == expected_origin for _, origin in loaded)
        names = {name for name, _ in loaded}
        assert {
            "sim.app.sugarscape.Sugarscape",
            "sim.app.sugarscape.Agent",
            "sim.engine.Schedule",
            "ec.util.MersenneTwisterFast",
        } <= names
        provenance.append(
            {
                "repeat": repeat,
                "original_model_framework_classes_loaded": sorted(names),
                "class_loading_log_sha256": hashlib.sha256(
                    (root / (stem + ".classes.log")).read_bytes()
                ).hexdigest(),
            }
        )
    population = (root / (config + "-observer-population.csv")).read_bytes()
    assert population == gzip.decompress(
        (old / (config + "-observer-population.csv.gz")).read_bytes()
    )
    states = list(csv.DictReader(population.decode().splitlines()))
    assert len(states) == 1002
    mismatches = [
        r
        for r in states
        if len(
            {
                r[k]
                for k in [
                    "reported_population",
                    "grid_alive",
                    "registered",
                    "registered_alive",
                ]
            }
        )
        != 1
    ]
    reports.append(
        {
            "configuration": config,
            "seed": 0,
            "scheduled_time_limit": 1000,
            "runs": 3,
            "stdout_exactly_matches_source_rebuild": True,
            "repeat_and_observer_stdout_exact": True,
            "population_observer_exactly_matches_source_rebuild": True,
            "population_states": len(states),
            "disagreeing_population_states": len(mismatches),
            "first_disagreement": mismatches[:1],
            "last_state": states[-1],
            "stdout_sha256": hashlib.sha256(current).hexdigest(),
            "population_csv_sha256": hashlib.sha256(population).hexdigest(),
            "class_origins": provenance,
        }
    )
classes = {n: v for n, v in manifest["files"].items() if n.endswith(".class")}
for name, expected in classes.items():
    raw = (root / "native" / name).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == expected["sha256"]
    assert raw[:4] == bytes.fromhex("cafebabe")
assert sorted(p.name for p in (root / "wrappers").rglob("*.class")) == [
    "AuditReplay.class",
    "Replay.class",
]
report = {
    "archive_sha256": manifest["archive_sha256"],
    "bundled_class_files_verified": len(classes),
    "model_class_files": sum("/sim/app/sugarscape/" in n for n in classes),
    "compiled_wrapper_classes": 2,
    "author_source_classes_rebuilt": 0,
    "runs": reports,
    "scope": "Original bundled bytecode matches rebuilt release for three seed-zero 1000-time configurations. Existing accounting defects are not caused by modern recompilation in these checks. Same Java11 runtime; no historical JVM equivalence, earlier source recovery, or paper-level verdict.",
}
output.write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps({k: v for k, v in report.items() if k != "runs"}, indent=2))
print([(x["configuration"], x["disagreeing_population_states"]) for x in reports])
