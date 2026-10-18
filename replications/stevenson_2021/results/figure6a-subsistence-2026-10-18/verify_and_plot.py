from pathlib import Path
from decimal import Decimal
import csv
import json
import re
import xml.etree.ElementTree as ET
import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

root = Path(__file__).resolve().parent
paths = ET.parse(root / "extraction/figure6.svg").findall(
    ".//{http://www.w3.org/2000/svg}path"
)
errors = []
for index, f, kind in [
    (111, 10, "actual"),
    (124, 10, "fitted"),
    (125, 5, "actual"),
    (126, 5, "fitted"),
]:
    raw = re.findall(r"[ML] ([0-9.]+) ([0-9.]+)", paths[index].attrib["d"])
    with (root / "extraction" / f"infertility-{f}-{kind}.csv").open() as stream:
        rows = list(csv.DictReader(stream))
    for (x, y), r in zip(raw, rows, strict=True):
        time = (
            (Decimal(y) - Decimal("373.320312"))
            / (Decimal("2506.71875") - Decimal("373.320312"))
            * 200
        )
        pop = (
            (Decimal("2581.289062") - Decimal(x))
            / (Decimal("2581.289062") - Decimal("681.015625"))
            * 800
        )
        errors.extend(
            [
                abs(float(time) - float(r["approximate_cycle"])),
                abs(float(pop) - float(r["approximate_population"])),
            ]
        )
assert len(errors) == 2330 and max(errors) < 1e-9
(root / "independent-vector-audit.json").write_text(
    json.dumps(
        {
            "vertices": 1165,
            "coordinate_checks": len(errors),
            "maximum_absolute_difference": max(errors),
            "method": "Decimal arithmetic from raw SVG coordinates, independently compared with exported CSV calibration.",
        },
        indent=2,
    )
    + "\n"
)
fig, axes = plt.subplots(1, 2, figsize=(11, 4), sharey=True)
with np.load(root / "analysis/populations.npz") as archive:
    for ax, f in zip(axes, [5, 10], strict=True):
        samples = archive[f"infertility{f}"][:, :200]
        time = np.arange(1, 201)
        low, high = np.percentile(samples, [2.5, 97.5], axis=0)
        ax.fill_between(
            time, low, high, alpha=0.2, color="#2471a3", label="Pointwise 95% seed band"
        )
        ax.plot(time, samples.mean(axis=0), color="#2471a3", label="100-seed mean")
        with (root / "extraction" / f"infertility-{f}-actual.csv").open() as stream:
            rows = list(csv.DictReader(stream))
        selected = [r for r in rows if 1 <= round(float(r["approximate_cycle"])) <= 200]
        ax.scatter(
            [float(r["approximate_cycle"]) for r in selected],
            [float(r["approximate_population"]) for r in selected],
            s=7,
            color="#a93226",
            label="Published actual vertices",
        )
        ax.set(title=f"Infertility {f}; metabolism 4", xlabel="Cycle", xlim=(0, 200))
        ax.grid(alpha=0.2)
axes[0].set_ylabel("Population")
axes[1].legend(fontsize=8)
fig.suptitle("Figure 6(a): conditional reconstruction; author seed unknown")
fig.tight_layout()
fig.savefig(root / "comparison.png", dpi=160)
fig.savefig(root / "comparison.pdf")
plt.close(fig)
print(max(errors))
