"""Compare model sources beside deleted data with the selected author release."""

import argparse
import hashlib
import json
from pathlib import Path
import subprocess

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("engine", type=Path)
parser.add_argument("library", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
old = "26df7d9cbcd75bb8f87b860a593dbd626af0d25e"
new = "585e53398f4f58e89ec184c83bb20819f0e4c96a"
rows = []
for before, after in [
    ("Policy Network", "Policy-Network"),
    ("Policy-Explicit", "Policy-Explicit"),
]:
    paths = subprocess.check_output(
        ["git", "ls-tree", "-r", "--name-only", old, "--", before],
        cwd=args.engine,
        text=True,
    ).splitlines()
    for path in paths:
        if not path.endswith(".py"):
            continue
        target = after + path[len(before) :]
        a = subprocess.check_output(["git", "show", f"{old}:{path}"], cwd=args.engine)
        b = subprocess.check_output(["git", "show", f"{new}:{target}"], cwd=args.engine)
        normalized = a
        changes = []
        if path.endswith("/NetScape.py"):
            assert a.count(b"from ml_mesa import ML_Mesa") == 1
            assert a.count(b"ML_Mesa(self)") == 1
            normalized = normalized.replace(
                b"from ml_mesa import ML_Mesa", b"import multilevel_mesa as mlm"
            )
            normalized = normalized.replace(
                b"ML_Mesa(self)", b"mlm.MultiLevel_Mesa(self)"
            )
            changes.append("Library import and constructor renamed")
            if before == "Policy-Explicit":
                assert a.count(b"itertools") == 1
                normalized = normalized.replace(b"import itertools\r\n", b"")
                changes.append("Unused itertools import removed")
        assert normalized == b, path
        rows.append(
            {
                "old_path": path,
                "new_path": target,
                "old_sha256": hashlib.sha256(a).hexdigest(),
                "new_sha256": hashlib.sha256(b).hexdigest(),
                "byte_identical": a == b,
                "declared_edits": changes,
                "exact_after_declared_edits": True,
            }
        )
assert len(rows) == 22
library_old = "9c0cf5f558e59f11dd915065aad4c930e44aa400"
library_new = "99d2091721076df9fff32e8b49a0e33e98c34a6f"
a = subprocess.check_output(
    ["git", "show", f"{library_old}:ml_mesa/ml_mesa.py"], cwd=args.library
)
b = subprocess.check_output(
    ["git", "show", f"{library_new}:multilevel_mesa/multilevel_mesa.py"],
    cwd=args.library,
)
normalized = a
for before, after in [
    (b"class ML_Mesa(RandomActivation):", b"class MultiLevel_Mesa(RandomActivation):"),
    (
        b"class GroupAgent(Agent, ML_Mesa):",
        b"class GroupAgent(Agent, MultiLevel_Mesa):",
    ),
]:
    assert a.count(before) == 1
    normalized = normalized.replace(before, after)
assert normalized == b
report = {
    "data_commit": old,
    "selected_model_revision": new,
    "model_python_files": rows,
    "byte_identical_model_files": sum(row["byte_identical"] for row in rows),
    "library": {
        "candidate_revision_before_data_commit": library_old,
        "selected_revision": library_new,
        "old_sha256": hashlib.sha256(a).hexdigest(),
        "new_sha256": hashlib.sha256(b).hexdigest(),
        "exact_after_two_class_name_edits": True,
    },
    "scope": "Static comparison of available source revisions. Twenty model files match byte-for-byte; two differ only by declared import/name edits and one unused import. The candidate library core differs only by two class-name edits. This does not identify the library actually loaded to generate the archived data, authenticate dependencies or RNG states, or prove numerical trajectory identity across runtimes.",
}
with args.output.open("x") as stream:
    stream.write(json.dumps(report, indent=2) + "\n")
print(
    json.dumps(
        {
            "model_files": len(rows),
            "byte_identical": report["byte_identical_model_files"],
            "declared_edits_only": True,
        }
    )
)
