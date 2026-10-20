"""Audit a complete observed initial world under explicit landscape parameters.

This checks states and landscape arithmetic, not the random generator, model-source
identity, or simulation transitions. Native provenance must be audited separately.
"""

import argparse
import csv
import hashlib
import json
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class InitialCell(BaseModel):
    model_config = ConfigDict(extra="forbid")
    step: Literal[-1]
    id: int
    x: int = Field(ge=0, lt=256)
    y: int = Field(ge=0, lt=256)
    status: Literal[0, 1]
    sugar: int
    metabolism: int
    cell_sugar: int = Field(ge=0)
    cell_capacity: int = Field(ge=0)


class InitialAudit(BaseModel):
    model_config = ConfigDict(extra="forbid")
    initial_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    peak_log_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    metabolism_maximum: Literal[4, 5]
    capacity_maximum: Literal[4, 7]
    geometry: Literal["direct", "wrapped"]
    cells: Literal[65536]
    peaks: Literal[54]
    occupied: int
    minimum_wrapped_peak_squared_distance: int
    peak_pairs_below_stated_spacing: int
    exact_capacity_matches: Literal[65536]
    total_initial_sugar: int
    maximum_initial_capacity: int
    scope: str


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("initial", type=Path)
    parser.add_argument("peak_log", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--metabolism", type=int, choices=[4, 5], required=True)
    parser.add_argument("--capacity", type=int, choices=[4, 7], required=True)
    parser.add_argument("--geometry", choices=["direct", "wrapped"], required=True)
    args = parser.parse_args()
    assert not args.output.exists()
    raw = args.initial.read_bytes()
    rows = [
        InitialCell.model_validate({key: int(value) for key, value in row.items()})
        for row in csv.DictReader(raw.decode().splitlines())
    ]
    assert len(rows) == 65536
    assert [(r.x, r.y) for r in rows] == [
        (x, y) for x in range(256) for y in range(256)
    ]
    active = [r for r in rows if r.status == 1]
    assert [r.id for r in active] == list(range(len(active)))
    assert all(
        5 <= r.sugar <= 25 and 1 <= r.metabolism <= args.metabolism for r in active
    )
    assert all(
        r.id == -1 and r.sugar == r.metabolism == 0 for r in rows if r.status == 0
    )
    assert all(r.cell_sugar == r.cell_capacity <= args.capacity for r in rows)
    peak_raw = args.peak_log.read_bytes()
    peaks = []
    for line in peak_raw.decode().splitlines():
        if line.startswith("HOTSPOT,"):
            kind, hx, hy = line.split(",")
            peaks.append((int(hx), int(hy)))
    assert len(peaks) == 54 and len(set(peaks)) == 54
    assert all(0 <= hx < 256 and 0 <= hy < 256 for hx, hy in peaks)
    separations = []
    for i, (hx, hy) in enumerate(peaks):
        for ox, oy in peaks[:i]:
            dx, dy = abs(hx - ox), abs(hy - oy)
            separations.append(min(dx, 256 - dx) ** 2 + min(dy, 256 - dy) ** 2)
    expected = []
    for cell in rows:
        total = 0
        for hx, hy in peaks:
            dx, dy = abs(cell.x - hx), abs(cell.y - hy)
            if args.geometry == "wrapped":
                dx, dy = min(dx, 256 - dx), min(dy, 256 - dy)
            squared = dx * dx + dy * dy
            total += (
                (squared < 25) + (squared < 100) + (squared < 225) + (squared < 400)
            )
        expected.append(min(args.capacity, total))
    assert expected == [r.cell_capacity for r in rows]
    report = InitialAudit(
        initial_sha256=hashlib.sha256(raw).hexdigest(),
        peak_log_sha256=hashlib.sha256(peak_raw).hexdigest(),
        metabolism_maximum=args.metabolism,
        capacity_maximum=args.capacity,
        geometry=args.geometry,
        cells=len(rows),
        peaks=len(peaks),
        occupied=len(active),
        minimum_wrapped_peak_squared_distance=min(separations),
        peak_pairs_below_stated_spacing=sum(d < 400 for d in separations),
        exact_capacity_matches=len(rows),
        total_initial_sugar=sum(expected),
        maximum_initial_capacity=max(expected),
        scope=__doc__,
    )
    args.output.write_text(report.model_dump_json(indent=2) + "\n")
    print(json.dumps(report.model_dump()))


if __name__ == "__main__":
    main()
