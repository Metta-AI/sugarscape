"""Extract Figure 6(b) and diagnose its discrete population recurrence."""

import argparse
import csv
import hashlib
import json
import re
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

import numpy as np

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("pdf", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
pdf_bytes = args.pdf.read_bytes()
assert (
    hashlib.sha256(pdf_bytes).hexdigest()
    == "d4e9c64d3792db28af5e0e7e4e2bb67206fcc81f7e94b85ba74d2b05d5aeadaf"
)
args.output.mkdir(parents=True, exist_ok=False)
svg = args.output / "figure6.svg"
subprocess.run(
    ["pdftocairo", "-svg", str(args.pdf.resolve()), str(svg.resolve())], check=True
)
paths = ET.parse(svg).findall(".//{http://www.w3.org/2000/svg}path")
# Original labeled ticks: time 0..80 and population 0..1000; PDF rotation exchanges axes.
assert paths[132].attrib["d"] == "M 2663.984375 3253.28125 L 2663.984375 5386.71875 "
assert paths[138].attrib["d"] == "M 2583.28125 3168.007812 L 622.695312 3168.007812 "
curves = []
for index, rate, dash in [
    (131, 0.025, "7.5 22.5 37.5 22.5"),
    (145, 0.47, "22.5 37.5"),
    (146, 2.0, "solid"),
    (147, 2.7, "0 30"),
]:
    path = paths[index]
    assert path.attrib["transform"] == "matrix(0.1, 0, 0, -0.1, 0, 576)"
    assert path.attrib["stroke"] == "rgb(0%, 0%, 0%)"
    if dash == "solid":
        assert "stroke-dasharray" not in path.attrib
    else:
        assert path.attrib["stroke-dasharray"] == dash
    encoded = path.attrib["d"]
    assert re.sub(r"[ML] [0-9.]+ [0-9.]+\s*", "", encoded) == ""
    points = [
        (
            (float(y) - 3253.28125) / (5386.71875 - 3253.28125) * 80,
            (2583.28125 - float(x)) / (2583.28125 - 622.695312) * 1000,
        )
        for x, y in re.findall(r"[ML] ([0-9.]+) ([0-9.]+)", encoded)
    ]
    assert all(a[0] < b[0] for a, b in zip(points, points[1:]))
    rounding_error = max(abs(t - round(t)) for t, _ in points)
    assert rounding_error < 0.01
    filename = f"rate-{rate:g}.csv"
    with (args.output / filename).open("x", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(["approximate_cycle", "approximate_population"])
        writer.writerows(points)
    # Preserve all exported vertices, but restrict inference to the labeled 0..80 window.
    # Do not interpolate omitted collinear vertices or invent a pre-initial history.
    values = {round(t): n for t, n in points if 1 <= round(t) <= 80}
    assert len(values) == sum(1 <= round(t) <= 80 for t, _ in points)
    diagnostics = []
    for delay in [0, 3]:
        rows = [
            (t, n, values[t + 1], values[t - delay])
            for t, n in values.items()
            if t + 1 in values and t - 3 in values
        ]
        current = np.array([row[1] for row in rows])
        following = np.array([row[2] for row in rows])
        lagged = np.array([row[3] for row in rows])
        assert len(rows) > 0 and (current > 0).all()
        # Fit b in N(t+1)=N(t)*(1+r-b*N(t-delay)); r remains the printed label.
        # Least squares uses population residuals, avoiding division by tiny populations.
        x = current * lagged
        y = current * (1 + rate) - following
        coefficient = float(np.dot(x, y) / np.dot(x, x))
        residual = following - current * (1 + rate - coefficient * lagged)
        assert coefficient > 0 and np.isfinite(residual).all()
        diagnostics.append(
            {
                "delay": delay,
                "observed_transition_count": len(rows),
                "fitted_density_coefficient": coefficient,
                "implied_K_printed_equation": 1 / coefficient,
                "implied_K_with_r_in_density_term": rate / coefficient,
                "population_residual_rms": float(np.sqrt(np.mean(residual**2))),
                "population_residual_max_abs": float(np.max(np.abs(residual))),
            }
        )
    curves.append(
        {
            "rate_label": rate,
            "svg_path_index": index,
            "vertices": len(points),
            "maximum_cycle_rounding_error": rounding_error,
            "csv_sha256": hashlib.sha256(
                (args.output / filename).read_bytes()
            ).hexdigest(),
            "diagnostics": diagnostics,
        }
    )
report = {
    "pdf_sha256": hashlib.sha256(pdf_bytes).hexdigest(),
    "svg_sha256": hashlib.sha256(svg.read_bytes()).hexdigest(),
    "analyzer_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    "curves": curves,
    "method": "Original vector coordinates calibrated from labeled axes. Fit one density coefficient per curve and delay with rate fixed to its legend. Use the same observed transitions for both delays, requiring vertices at t-3, t, and t+1 in 1..80.",
    "limitations": "Descriptive equation diagnostic, not independent prediction or simulation replication. K is fitted, not a published input. Rounded coordinates and omitted collinear points limit precision. Low-rate population remains tiny and its density coefficient is poorly identified. No evolutionary rules or Figure 6(a) agent model are recovered.",
}
(args.output / "audit.json").write_text(
    json.dumps(report, indent=2, allow_nan=False) + "\n"
)
print(json.dumps(curves, indent=2))
