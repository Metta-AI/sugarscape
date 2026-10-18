"""Recover Figure 8 cell capacities and compare retained NetLogo map files."""

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("maps", type=Path, nargs="+")
parser.add_argument("--output", type=Path, required=True)
args = parser.parse_args()
figure = Path(__file__).with_name("Fig8-sugar-map.png")
image = np.asarray(Image.open(figure).convert("RGB"))
assert image.shape == (300, 300, 3)
# Table 8 maps increasingly dark regions to sugar capacities 0 through 4.
# Use exact RGB palette matches; antialiased labels include 40 non-gray pixels.
colors = Counter(map(tuple, image.reshape(-1, 3)))
palette = sorted((color for color, count in colors.most_common(5)), reverse=True)
levels = [109, 82, 57, 34, 14]
assert palette == [(level, level, level) for level in levels]
grid = np.empty((50, 50), dtype=int)
support = []
for y in range(50):
    for x in range(50):
        block = Counter(
            map(tuple, image[y * 6 : (y + 1) * 6, x * 6 : (x + 1) * 6].reshape(-1, 3))
        )
        counts = [block[color] for color in palette]
        capacity = int(np.argmax(counts))
        ranked = sorted(counts, reverse=True)
        assert ranked[0] > ranked[1]
        grid[y, x] = capacity
        support.append(
            {"row": y, "column": x, "capacity": capacity, "palette_support": counts}
        )
comparisons = []
for path in args.maps:
    candidate = np.loadtxt(path, dtype=int)
    assert candidate.shape == (50, 50)
    orientations = []
    for quarter_turns in range(4):
        rotated = np.rot90(candidate, quarter_turns)
        for reflected in [False, True]:
            transformed = np.fliplr(rotated) if reflected else rotated
            orientations.append(
                {
                    "quarter_turns_ccw": quarter_turns,
                    "horizontal_reflection": reflected,
                    "different_cells": int(np.count_nonzero(transformed != grid)),
                }
            )
    assert orientations[0]["different_cells"] == 0
    comparisons.append(
        {
            "path": str(path),
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "orientations": orientations,
        }
    )
args.output.mkdir(parents=True, exist_ok=False)
np.savetxt(args.output / "figure8-capacity.txt", grid, fmt="%d")
report = {
    "paper_url": "https://www.jasss.org/17/2/6.html",
    "figure_url": "https://www.jasss.org/17/2/6/Fig8-sugar-map.png",
    "figure_sha256": hashlib.sha256(figure.read_bytes()).hexdigest(),
    "capacity_matrix_sha256": hashlib.sha256(
        (args.output / "figure8-capacity.txt").read_bytes()
    ).hexdigest(),
    "shape": [50, 50],
    "pixels_per_cell": [6, 6],
    "non_gray_label_pixels": int(np.any(image != image[:, :, :1], axis=2).sum()),
    "grayscale_levels_for_capacity_0_to_4": levels,
    "minimum_winning_palette_pixels_per_cell": min(
        max(row["palette_support"]) for row in support
    ),
    "minimum_margin_over_next_palette_color": min(
        sorted(row["palette_support"], reverse=True)[0]
        - sorted(row["palette_support"], reverse=True)[1]
        for row in support
    ),
    "capacity_cell_counts": {
        str(capacity): int(np.count_nonzero(grid == capacity)) for capacity in range(5)
    },
    "comparisons": comparisons,
    "scope": "All 2,500 Figure 8 cells agree exactly with each retained NetLogo capacity matrix, in native file row order. Figure labels overlay pixels; capacities use the dominant palette color within each 6x6 cell. This resolves the published 50x50 capacity layout, not the original author file identity, resampling convention, tax implementation, or simulation results.",
}
(args.output / "comparison.json").write_text(json.dumps(report, indent=2) + "\n")
(args.output / "cell-support.json").write_text(
    json.dumps(support, separators=(",", ":")) + "\n"
)
print(json.dumps(report))
