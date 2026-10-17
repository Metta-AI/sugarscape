"""Expose the paper's five-versus-ten trade threshold without changing resource rules."""

import argparse
import hashlib
import importlib
import json
from pathlib import Path
import runpy
import sys

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("engine", type=Path)
parser.add_argument("library", type=Path)
parser.add_argument("variant", choices=["common-one", "common-multi"])
parser.add_argument("threshold", type=int, choices=[5, 10])
parser.add_argument("seed", type=int)
parser.add_argument("output", type=Path)
args = parser.parse_args()
source = (
    args.engine.resolve()
    / {
        "common-one": "Common Resource- one level",
        "common-multi": "Common Resource- multi-level",
    }[args.variant]
)
sys.path[:0] = [str(source), str(args.library.resolve())]
organization = importlib.import_module("organization")
MultiLevel_Mesa = importlib.import_module(
    "multilevel_mesa.multilevel_mesa"
).MultiLevel_Mesa

native_group = MultiLevel_Mesa.net_group
calls = 0


def configured_group(self, link_type=None, link_value=None, double=False, policy=None):
    global calls
    assert link_type == "trades" and link_value == 10 and not double
    assert policy is organization.rules
    calls += 1
    return native_group(
        self,
        link_type=link_type,
        link_value=args.threshold,
        double=double,
        policy=policy,
    )


MultiLevel_Mesa.net_group = configured_group
args.output.mkdir(parents=True, exist_ok=False)
(args.output / "configuration.json").write_text(
    json.dumps(
        {
            "variant": args.variant,
            "threshold": args.threshold,
            "seed": args.seed,
            "steps": 1000,
            "adapter_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "scope": "Only native net_group link_value changes; released common-resource rules retained.",
        },
        indent=2,
    )
    + "\n"
)
runner = Path(__file__).with_name("run.py")
sys.argv = [
    str(runner),
    str(args.engine),
    str(args.library),
    args.variant,
    str(args.seed),
    str(args.output / "run"),
]
runpy.run_path(str(runner), run_name="__main__")
assert calls == 1000
(args.output / "parameterization-complete.json").write_text(
    json.dumps({"grouping_calls": calls}) + "\n"
)
