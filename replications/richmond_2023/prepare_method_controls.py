"""Prepare pinned, separately labelled rule controls without modifying author sources."""

import argparse
import difflib
import hashlib
import json
from pathlib import Path
import subprocess

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("source", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
revision = "290702073492677f2fc9164419e9d5900d119e02"
assert (
    subprocess.check_output(
        ["git", "-C", str(args.source), "rev-parse", "HEAD"], text=True
    ).strip()
    == revision
)
original = (args.source / "src/main.cu").read_bytes()
assert hashlib.sha256(original).hexdigest() == (
    "b2daf9e6ee2b3faf4a13e30ba19f4293e1f922a993d30cb5e72fb1d4c2b8f56d"
)
text = original.decode()
changes = {
    "transfer": (
        "                    best_request_priority = message_priority;",
        '                    best_request_sugar_level = current_message.getVariable<int>("sugar_level");\n'
        '                    best_request_metabolism = current_message.getVariable<int>("metabolism");\n'
        "                    best_request_priority = message_priority;",
        1,
    ),
    "cardinal": (
        "FLAMEGPU->message_in.wrap(agent_x, agent_y)",
        "FLAMEGPU->message_in.vn_wrap(agent_x, agent_y)",
        3,
    ),
    "nonpositive_death": ("if (sugar_level == 0)", "if (sugar_level <= 0)", 1),
}
for old, new, count in changes.values():
    assert text.count(old) == count and new not in text
args.output.mkdir(parents=True, exist_ok=False)
records = []
for variant, rules in [
    ("released", []),
    ("transfer", ["transfer"]),
    ("cardinal", ["cardinal"]),
    ("nonpositive_death", ["nonpositive_death"]),
    ("combined_three_rules", list(changes)),
]:
    modified = text
    for rule in rules:
        old, new, count = changes[rule]
        assert modified.count(old) == count
        modified = modified.replace(old, new)
    restored = modified
    for rule in reversed(rules):
        old, new, count = changes[rule]
        assert restored.count(new) == count
        restored = restored.replace(new, old)
    assert restored.encode() == original
    directory = args.output / variant
    directory.mkdir()
    payload = modified.encode()
    (directory / "main.cu").write_bytes(payload)
    patch = "".join(
        difflib.unified_diff(
            text.splitlines(keepends=True),
            modified.splitlines(keepends=True),
            fromfile="a/src/main.cu",
            tofile="b/src/main.cu",
        )
    )
    (directory / "rules.patch").write_text(patch)
    records.append(
        {
            "variant": variant,
            "rules": rules,
            "source_sha256": hashlib.sha256(payload).hexdigest(),
            "patch_sha256": hashlib.sha256(patch.encode()).hexdigest(),
            "reverse_edits_byte_exact": True,
        }
    )
report = {
    "source_revision": revision,
    "original_sha256": hashlib.sha256(original).hexdigest(),
    "variants": records,
    "scope": "Source preparation only. No compilation, native execution, or method-completion credit.",
    "unchanged": [
        "initialization and landscape",
        "random generator and seed",
        "resolution exit counter and nine-iteration cap",
        "timing and population reporters",
    ],
}
(args.output / "manifest.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report))
