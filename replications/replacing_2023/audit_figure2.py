"""Decode Figure 2 vector vertices using its labeled axes and compare native counts."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import xml.etree.ElementTree as ET

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("pdf", type=Path)
parser.add_argument("baseline", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
targets = json.loads(Path(__file__).with_name("published_targets.json").read_text())
assert hashlib.sha256(args.pdf.read_bytes()).hexdigest() == targets["pdf_sha256"]
args.output.mkdir(parents=True, exist_ok=False)
svg = args.output / "page9.svg"
command = ["pdftocairo", "-svg", "-f", "9", "-l", "9", str(args.pdf.resolve()), str(svg.resolve())]
subprocess.run(command, check=True)
paths = ET.parse(svg).findall('.//{http://www.w3.org/2000/svg}path')
curves = [p for p in paths if "stroke" in p.attrib and len(p.attrib["d"]) > 10000]
assert len(curves) == 1
curve = curves[0]
vertices = [(float(x), float(y)) for x, y in re.findall(r'[ML] ([0-9.]+) ([0-9.]+)', curve.attrib["d"])]
assert re.sub(r'[ML] [0-9.]+ [0-9.]+\s*', '', curve.attrib["d"]) == ""
# These coordinates identify the plotted rectangle, not a fit to simulation output.
# Its inspected tick labels are x=0..2500 and y=300..1200 on PDF page9.
x0, x1, y0, y1 = 63.815034, 339.501805, 172.844477, 13.838655
rectangles = [p for p in paths if "stroke" in p.attrib and " Z " in p.attrib["d"]]
assert len(rectangles) == 2 and rectangles[0].attrib["d"] == rectangles[1].attrib["d"]
assert rectangles[0].attrib["d"].startswith(f"M {x0} {y1} L {x1} {y1} L {x1} {y0} L {x0} {y0} Z")
assert rectangles[0].attrib["transform"] == curve.attrib["transform"]
raw = (args.baseline / "trajectory.json").read_bytes()
result = json.loads((args.baseline / "result.json").read_text())
assert hashlib.sha256(raw).hexdigest() == result["trajectory_sha256"]
rows = json.loads(raw)
assert [r["timestep"] for r in rows] == list(range(2501))
assert all(r["seed"] == targets["baseline_seed"] for r in rows)
comparison = []
for x, y in vertices:
    t = (x - x0) / (x1 - x0) * 2500
    population = 300 + (y0 - y) / (y0 - y1) * 900
    step, count = round(t), round(population)
    assert 0 <= step <= 2500 and 300 <= count <= 1200
    comparison.append({"step": step, "figure_population_rounded": count,
        "native_population": rows[step]["population"], "matches": count == rows[step]["population"],
        "timestep_rounding_distance": abs(t - step), "population_rounding_distance": abs(population - count)})
assert len({r["step"] for r in comparison}) == len(comparison)
report = {"pdf_sha256": targets["pdf_sha256"], "svg_sha256": hashlib.sha256(svg.read_bytes()).hexdigest(),
    "trajectory_sha256": result["trajectory_sha256"], "command": command,
    "vertices": len(comparison), "matching_vertices": sum(r["matches"] for r in comparison),
    "unrepresented_timesteps": sorted(set(range(2501)) - {r["step"] for r in comparison}),
    "maximum_timestep_rounding_distance": max(r["timestep_rounding_distance"] for r in comparison),
    "maximum_population_rounding_distance": max(r["population_rounding_distance"] for r in comparison),
    "comparison": comparison,
    "interpretation": "Axes calibrated from inspected figure labels and rectangle; not fitted to simulation. Integer rounding recovers represented vertices only. Missing vertices are not claimed observed. Figure agreement does not validate Table3 labels or the prose's60–100dip timing."}
(args.output / "audit.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps({k: v for k, v in report.items() if k not in ["comparison", "unrepresented_timesteps"]}))
assert all(r["matches"] for r in comparison), "Figure vertex mismatch; inspect retained report"
