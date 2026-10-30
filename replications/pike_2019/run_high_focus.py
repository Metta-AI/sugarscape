"""Run a separately identified high-focus comparator correction."""

import argparse
import hashlib
import json
import runpy
import sys
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("engine", type=Path)
parser.add_argument("library", type=Path)
parser.add_argument("approach", choices=["explicit", "network"])
parser.add_argument("threshold", type=int, choices=[1, 5, 10])
parser.add_argument("seed", type=int)
parser.add_argument("output", type=Path)
args = parser.parse_args()
source = (
    args.engine.resolve()
    / {"explicit": "Policy-Explicit", "network": "Policy-Network"}[args.approach]
)
sys.path[:0] = [str(source), str(args.library.resolve())]
import correct_high_focus

args.output.mkdir(parents=True, exist_ok=False)
(args.output / "original-step-high.py").write_text(correct_high_focus.original_source)
(args.output / "corrected-step-high.py").write_text(correct_high_focus.corrected_source)
(args.output / "correction.json").write_text(
    json.dumps(
        {
            "scope": "Only reverse max(highest) > max(new) to < in step_high; historical paper revision unverified.",
            "module_sha256": hashlib.sha256(
                Path(correct_high_focus.__file__).read_bytes()
            ).hexdigest(),
            "runner_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        },
        indent=2,
    )
    + "\n"
)
runner = Path(__file__).with_name("run_groups.py")
sys.argv = [
    str(runner),
    str(args.engine),
    str(args.library),
    args.approach,
    str(args.threshold),
    "movement",
    str(args.seed),
    str(args.output / "configured"),
]
runpy.run_path(str(runner), run_name="__main__")
