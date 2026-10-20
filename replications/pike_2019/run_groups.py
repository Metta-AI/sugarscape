"""Parameterize the paper's group thresholds and optional movement policy."""

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
parser.add_argument("policy", choices=["none", "movement"])
parser.add_argument("seed", type=int)
parser.add_argument("output", type=Path)
args = parser.parse_args()
source = (
    args.engine.resolve()
    / {"explicit": "Policy-Explicit", "network": "Policy-Network"}[args.approach]
)
sys.path[:0] = [str(source), str(args.library.resolve())]
import organization
from multilevel_mesa.multilevel_mesa import MultiLevel_Mesa

calls = 0
policy = organization.rules if args.policy == "movement" else None
if args.approach == "network":
    native_group = MultiLevel_Mesa.net_group

    def configured_group(
        self, link_type=None, link_value=None, double=False, policy=None
    ):
        global calls
        assert (
            link_type == "trades" and link_value == 10 and not double and policy is None
        )
        calls += 1
        return native_group(
            self,
            link_type="trades",
            link_value=args.threshold,
            double=False,
            policy=organization.rules if args.policy == "movement" else None,
        )

    MultiLevel_Mesa.net_group = configured_group
else:
    import apto_processes

    native_group = MultiLevel_Mesa.form_group

    def threshold_connections(model):
        for agent, trades in model.trades.items():
            agents = [agent]
            for partner, count in trades.items():
                if count >= args.threshold:
                    agents.append(partner)
            if len(agents) > 1:
                yield agents

    def configured_group(self, process, model, **kwargs):
        global calls
        assert process is apto_processes.form_connection_group
        assert kwargs == {"policy": organization.rules}
        calls += 1
        return native_group(self, threshold_connections, model, policy=policy)

    MultiLevel_Mesa.form_group = configured_group

args.output.mkdir(parents=True, exist_ok=False)
configuration = {
    "approach": args.approach,
    "threshold": args.threshold,
    "policy": args.policy,
    "seed": args.seed,
    "steps": 1000,
    "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    "scope": "Declared threshold/policy parameterization; no shared-resource corrections.",
}
(args.output / "configuration.json").write_text(
    json.dumps(configuration, indent=2) + "\n"
)
runner = Path(__file__).with_name("run.py")
sys.argv = [
    str(runner),
    str(args.engine),
    str(args.library),
    "groups-network" if args.approach == "network" else "policy-explicit",
    str(args.seed),
    str(args.output / "run"),
]
runpy.run_path(str(runner), run_name="__main__")
assert calls == 1000
(args.output / "parameterization-complete.json").write_text(
    json.dumps({"grouping_calls": calls}) + "\n"
)
