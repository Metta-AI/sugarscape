"""Stream every spatial frame and verify exact parity with prior sampled runs."""

import csv
import hashlib
import itertools
import json
import math
import sys
from pathlib import Path

root, prior, output = map(Path, sys.argv[1:])
p = json.loads((root / "protocol.json").read_text())
assert (root / "binary-sha256.txt").read_text().split()[0] == p["binary_sha256"]
assert (root / "exit-code.txt").read_text().strip() == "0"
assert json.loads((root / "complete.json").read_text()) == {"completed_cases": 2}
assert (
    hashlib.sha256((prior / "protocol.json").read_bytes()).hexdigest()
    == p["prior_protocol_sha256"]
)
assert (
    hashlib.sha256((prior / "observe").read_bytes()).hexdigest() == p["binary_sha256"]
)
assert (
    hashlib.sha256((prior / "Observe.hs").read_bytes()).hexdigest()
    == p["observer_sha256"]
)
for name, digest in p["source_sha256"].items():
    assert hashlib.sha256((prior / "source" / name).read_bytes()).hexdigest() == digest
results = []
for name, constructor in p["cases"]:
    spatial, old = root / "spatial", prior / "spatial"
    assert (
        (spatial / f"{name}.scenario.txt")
        .read_text()
        .startswith(f"Constructor: {constructor}\nSeed: {p['seed']}\n")
    )
    for suffix in ["scenario.txt", "summary.csv"]:
        assert (spatial / f"{name}.{suffix}").read_bytes() == (
            old / f"{name}.{suffix}"
        ).read_bytes()
    assert not (spatial / f"{name}.stdout.log").read_bytes()
    assert not (spatial / f"{name}.stderr.log").read_bytes()
    with (spatial / f"{name}.summary.csv").open() as stream:
        summaries = list(csv.DictReader(stream))
    assert [int(r["time"]) for r in summaries] == list(range(1001))
    assert all(math.isfinite(float(v)) for r in summaries for v in r.values())
    with (spatial / f"{name}.trades.csv").open() as stream:
        assert not list(csv.DictReader(stream))
    profiles = []
    agent_count = cell_count = 0
    previous_ids = set(range(1, 301))
    with (
        (spatial / f"{name}.agents.csv").open() as agents_file,
        (spatial / f"{name}.cells.csv").open() as cells_file,
        (old / f"{name}.agents.csv").open() as old_agents_file,
        (old / f"{name}.cells.csv").open() as old_cells_file,
    ):
        agents = itertools.groupby(
            csv.DictReader(agents_file), key=lambda r: int(r["time"])
        )
        cells = itertools.groupby(
            csv.DictReader(cells_file), key=lambda r: int(r["time"])
        )
        old_agents = itertools.groupby(
            csv.DictReader(old_agents_file), key=lambda r: int(r["time"])
        )
        old_cells = itertools.groupby(
            csv.DictReader(old_cells_file), key=lambda r: int(r["time"])
        )
        for step, ((at, ar), (ct, cr)) in enumerate(zip(agents, cells, strict=True)):
            assert step == at == ct
            a, c = list(ar), list(cr)
            assert all(
                math.isfinite(float(v))
                for r in a
                for k, v in r.items()
                if k != "culture"
            )
            assert all(math.isfinite(float(v)) for r in c for v in r.values())
            positions = {int(r["id"]): (int(r["x"]), int(r["y"])) for r in a}
            coords = {(int(r["x"]), int(r["y"])) for r in c}
            assert (
                len(a)
                == len(positions)
                == len(set(positions.values()))
                == int(summaries[step]["population"])
            )
            assert set(positions) <= previous_ids
            previous_ids = set(positions)
            assert len(c) == len(coords) == 2601
            assert all(0 <= v < 51 for xy in coords for v in xy)
            occupied = {
                int(r["occupier"]): (int(r["x"]), int(r["y"]))
                for r in c
                if int(r["occupier"]) >= 0
            }
            assert len(occupied) == sum(int(r["occupier"]) >= 0 for r in c)
            assert occupied == positions
            for resource in ["sugar", "spice"]:
                for rows, prefix in [(a, "agent_"), (c, "environment_")]:
                    assert math.isclose(
                        sum(float(r[resource]) for r in rows),
                        float(summaries[step][prefix + resource]),
                        rel_tol=1e-12,
                        abs_tol=1e-8,
                    )
            assert (
                sum(float(r["pollution"]) for r in c)
                == float(summaries[step]["pollution"])
                == 0
            )
            if step % 10 == 0:
                oat, oar = next(old_agents)
                oct_, ocr = next(old_cells)
                assert oat == oct_ == step and a == list(oar) and c == list(ocr)
            diagonal = [0] * 101
            for xy in positions.values():
                diagonal[sum(xy)] += 1
            profiles.append(
                {"time": step, "population": len(a), "diagonal_agent_counts": diagonal}
            )
            agent_count += len(a)
            cell_count += len(c)
        assert len(profiles) == 1001
        assert list(old_agents) == list(old_cells) == []
    hashes = {}
    for path in sorted(spatial.glob(name + ".*")):
        with path.open("rb") as stream:
            hashes[path.name] = hashlib.file_digest(stream, "sha256").hexdigest()
    results.append(
        {
            "case": name,
            "frames": len(profiles),
            "agent_observations": agent_count,
            "cell_observations": cell_count,
            "summary_rows_exact": 1001,
            "prior_spatial_frames_exact": 101,
            "occupancy_disagreements": 0,
            "profiles": profiles,
            "sha256": hashes,
        }
    )
report = {
    "source_hashes_verified": len(p["source_sha256"]),
    "cases": results,
    "scope": (
        "Repeated inputs at full temporal resolution; no added ensemble samples, "
        "fitted wave criterion, or completed-paper verdict."
    ),
}
with output.open("x") as stream:
    json.dump(report, stream, indent=2, allow_nan=False)
print(
    json.dumps(
        [
            {k: v for k, v in r.items() if k not in ["profiles", "sha256"]}
            for r in results
        ]
    )
)
