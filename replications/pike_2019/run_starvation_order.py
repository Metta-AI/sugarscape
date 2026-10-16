"""Sensitivity experiment: check group-member death after metabolism."""

import argparse
import hashlib
import importlib.metadata
import json
import platform
import runpy
import sys
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("engine", type=Path)
parser.add_argument("library", type=Path)
parser.add_argument("variant", choices=["common-one", "common-multi"])
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
import organization
import shared_pool


def consume_then_check(self, agent, meta):
    agent.accumulations = self.accumulations
    agent.eat()
    self.accumulations = agent.accumulations
    agent.die()
    if agent.status == "dead":
        return
    self.group_trade(agent, meta)


organization.rules.sub_step2 = consume_then_check
args.output.mkdir(parents=True, exist_ok=False)
(args.output / "sensitivity.json").write_text(
    json.dumps(
        {
            "scope": "Death after metabolism instead of before; shared balances and network-node correction retained. Experimental sensitivity, not historical paper fidelity.",
            "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "pool_correction_sha256": hashlib.sha256(
                Path(shared_pool.__file__).read_bytes()
            ).hexdigest(),
            "python": platform.python_version(),
            "packages": {
                name: importlib.metadata.version(name)
                for name in ["Mesa", "numpy", "networkx", "pandas"]
            },
        },
        indent=2,
    )
    + "\n"
)
runner = Path(__file__).with_name("run_corrected.py")
sys.argv = [
    str(runner),
    str(args.engine),
    str(args.library),
    args.variant,
    str(args.seed),
    str(args.output / "run"),
]
runpy.run_path(str(runner), run_name="__main__")
