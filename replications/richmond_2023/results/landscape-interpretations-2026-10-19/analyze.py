"""Compare complete retained host worlds under explicit landscape interpretations."""

from pathlib import Path
import csv
import gzip
import hashlib
import json
import numpy as np

root = Path(__file__).resolve().parent
records = []
for label, folder, state_name, hotspot_name, audit_name in [
    (
        "macos-gcc",
        "initial-state-extraction-2026-10-17",
        "state.csv.gz",
        "stderr-002.log",
        "audit.json",
    ),
    (
        "macos-clang",
        "initial-image-comparison-2026-10-17",
        "state-clang.csv.gz",
        "hotspots-clang.log",
        "host-audit.json",
    ),
]:
    source = root.parent / folder
    raw = gzip.decompress((source / state_name).read_bytes())
    audit = json.loads((source / audit_name).read_bytes())
    assert hashlib.sha256(raw).hexdigest() == audit["states_sha256"]
    hotspots_raw = (source / hotspot_name).read_bytes()
    assert hashlib.sha256(hotspots_raw).hexdigest() == audit["hotspots_sha256"]
    rows = list(csv.DictReader(raw.decode().splitlines()))
    assert len(rows) == 65536
    assert [(int(r["x"]), int(r["y"])) for r in rows] == [
        (x, y) for x in range(256) for y in range(256)
    ]
    hotspots = [
        tuple(map(int, line.split(",")[1:]))
        for line in hotspots_raw.decode().splitlines()
    ]
    assert len(hotspots) == 54
    pair_distances = []
    for i, (hx, hy) in enumerate(hotspots):
        for ox, oy in hotspots[:i]:
            dx, dy = abs(hx - ox), abs(hy - oy)
            pair_distances.append(min(dx, 256 - dx) ** 2 + min(dy, 256 - dy) ** 2)
    assert min(pair_distances) >= 400
    x, y = np.indices((256, 256))
    surfaces = {}
    for geometry in ["direct", "wrapped"]:
        total = np.zeros((256, 256), dtype=np.int64)
        for hx, hy in hotspots:
            dx, dy = np.abs(x - hx), np.abs(y - hy)
            if geometry == "wrapped":
                dx, dy = np.minimum(dx, 256 - dx), np.minimum(dy, 256 - dy)
            distance = np.sqrt(
                dx.astype(np.float64) ** 2 + dy.astype(np.float64) ** 2
            ).astype(np.float32)
            total += 4 - np.minimum(
                4, np.floor(distance / np.float32(5)).astype(np.int64)
            )
        surfaces[geometry + "_sum"] = total
        for cap in [4, 7]:
            surfaces[f"{geometry}_cap{cap}"] = np.minimum(cap, total)
    native = np.array([int(r["cell_capacity"]) for r in rows]).reshape(256, 256)
    assert np.array_equal(native, surfaces["direct_cap4"])
    columns = ["x", "y", *surfaces]
    data = np.column_stack(
        [x.ravel(), y.ravel(), *[v.ravel() for v in surfaces.values()]]
    )
    with gzip.open(root / (label + "-cells.csv.gz"), "wt") as stream:
        np.savetxt(
            stream, data, fmt="%d", delimiter=",", header=",".join(columns), comments=""
        )
    record = {
        "world": label,
        "source_folder": folder,
        "states_file": state_name,
        "hotspots_file": hotspot_name,
        "states_sha256": audit["states_sha256"],
        "hotspots_sha256": audit["hotspots_sha256"],
        "minimum_wrapped_peak_squared_distance": min(pair_distances),
        "cells": 65536,
        "metrics": {},
    }
    for name, values in surfaces.items():
        record["metrics"][name] = {
            "total_sugar": int(values.sum()),
            "maximum": int(values.max()),
            "cells_above_four": int((values > 4).sum()),
            "cells_different_from_released": int((values != native).sum()),
            "added_sugar_vs_released": int((values - native).sum()),
        }
    records.append(record)
(root / "analysis.json").write_text(
    json.dumps(
        {
            "records": records,
            "scope": "Posthoc initial-landscape sensitivity on two previously retained macOS host worlds. Not new independent seeds, native GPU controls, historical image matches, or a uniquely specified paper implementation.",
        },
        indent=2,
    )
    + "\n"
)
print(json.dumps(records, indent=2))
