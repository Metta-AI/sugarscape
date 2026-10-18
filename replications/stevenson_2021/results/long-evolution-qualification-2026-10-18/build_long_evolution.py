"""Suppress event exports while preserving the qualified evolutionary dynamics."""

import argparse
import difflib
import hashlib
from pathlib import Path
import subprocess
import sys

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("output", type=Path)
args = parser.parse_args()
subprocess.run(
    [
        sys.executable,
        str(Path(__file__).with_name("build_evolution.py")),
        str(args.output),
    ],
    check=True,
)
p = args.output / "simulate_evolution.cpp"
original = p.read_text()
source = original
birth = "                    traits << cycle << \",birth,\" << child.id << ',' << parent_id << ',' << child.infertility << ',' << child.birth_cost << \",1\\n\";"
for before, after in [
    ("                    const auto parent_id = agent.id;\n", ""),
    ("                    const auto& child = agents.back();\n", ""),
    (birth, ""),
    (
        "        record_traits(cycle, agents);",
        "        if (cycle % record_every == 0 || cycle == 1 || cycle == cycles || agents.empty()) record_traits(cycle, agents);",
    ),
]:
    assert source.count(before) == 1, before
    source = source.replace(before, after)
(args.output / "simulate_long_evolution.cpp").write_text(source)
(args.output / "observation-only.patch").write_text(
    "".join(
        difflib.unified_diff(
            original.splitlines(True),
            source.splitlines(True),
            fromfile="simulate_evolution.cpp",
            tofile="simulate_long_evolution.cpp",
        )
    )
)
print(hashlib.sha256(source.encode()).hexdigest())
