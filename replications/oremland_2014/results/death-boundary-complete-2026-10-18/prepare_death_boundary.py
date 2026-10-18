"""Prepare a paired Algorithm 3 death-rule diagnostic from retained requests."""

import argparse
import difflib
import hashlib
import json
from pathlib import Path
import shutil

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("reference", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
reference = args.reference.resolve()
root = args.output.resolve()
root.mkdir(exist_ok=False)
protocol = json.loads((reference / "protocol.json").read_text())
assert protocol["native_runs"] == 37600
protocol["paired_reference_protocol_sha256"] = hashlib.sha256(
    (reference / "protocol.json").read_bytes()
).hexdigest()
protocol["request_generator_sha256"] = protocol.pop("generator_sha256")
protocol["preparation_sha256"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
protocol["death_boundary"] = "negative"
protocol["target"] = "Paired post hoc diagnostic of conflicting printed death rules."
protocol["source_conflict"] = {
    "article": "https://www.jasss.org/17/2/6.html",
    "algorithm": "https://www.jasss.org/17/2/6/algorithm3.png",
    "prose_rule": "Agents die at zero sugar (Appendix B).",
    "algorithm_rule": "Agents die below zero sugar (Algorithm 3, line 19).",
}
protocol["analysis_declared_before_execution"] = [
    "Pair every request with its retained nonpositive-death result; change only the death comparison.",
    "Compare independent 50x50 and 40x40 groups with their own negative-death 50x50 reference.",
    "Retain both clocks, all budget prefixes, strata, tie conventions, and kappa weights.",
    "Report deaths, literal revenue, and positive payments on the literal trajectory. Adding refunds does not represent a clipped-payment counterfactual when zero-sugar agents survive.",
    "Neither printed rule is established author-code behavior. No negative replication or paper completion follows from this sensitivity alone.",
]
protocol["model_changes"] = []
for name in sorted({job["model"] for job in protocol["jobs"]}):
    shutil.copytree(reference / name, root / name)
    model = root / name / "oremland.nlogo"
    before = model.read_text()
    assert before.count("ask turtles with [sugar <= 0] [die]") == 1
    after = before.replace(
        "ask turtles with [sugar <= 0] [die]", "ask turtles with [sugar < 0] [die]"
    )
    model.write_text(after)
    (model.parent / "death-boundary.patch").write_text(
        "".join(
            difflib.unified_diff(
                before.splitlines(True),
                after.splitlines(True),
                fromfile="prose-rule.nlogo",
                tofile="algorithm-rule.nlogo",
            )
        )
    )
    digest = hashlib.sha256(model.read_bytes()).hexdigest()
    protocol["model_changes"].append(
        {
            "model": name,
            "before_sha256": hashlib.sha256(
                (reference / name / "oremland.nlogo").read_bytes()
            ).hexdigest(),
            "after_sha256": digest,
        }
    )
    for job in protocol["jobs"]:
        if job["model"] == name:
            job["model_sha256"] = digest
            assert (
                hashlib.sha256((root / job["requests"]).read_bytes()).hexdigest()
                == job["requests_gz_sha256"]
            )
for name in ["policies.json", "reduction-protocol.json"]:
    shutil.copy2(reference / name, root / name)
shutil.copy2(__file__, root / Path(__file__).name)
(root / "protocol.json").write_text(json.dumps(protocol, indent=2) + "\n")
print(root)
