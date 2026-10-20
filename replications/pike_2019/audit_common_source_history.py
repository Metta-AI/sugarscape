"""Compare common-resource model files across every ancestor of the selected revision."""

import argparse
import ast
import hashlib
import json
from pathlib import Path
import subprocess

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("engine", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
assert not args.output.exists()
revision = "585e53398f4f58e89ec184c83bb20819f0e4c96a"
commits = subprocess.check_output(
    ["git", "rev-list", "--reverse", revision], cwd=args.engine, text=True
).splitlines()
paths = [
    f"Common Resource- {level}/{name}"
    for level in ["one level", "multi-level"]
    for name in ["organization.py", "NetAgent.py"]
]
rows = []
for commit in commits:
    available = set(
        subprocess.check_output(
            ["git", "ls-tree", "-r", "--name-only", commit], cwd=args.engine, text=True
        ).splitlines()
    )
    metadata = subprocess.check_output(
        ["git", "show", "-s", "--format=%aI%n%cI%n%s", commit],
        cwd=args.engine,
        text=True,
    ).splitlines()
    files = []
    for path in paths:
        if path not in available:
            files.append({"path": path, "present": False})
            continue
        raw = subprocess.check_output(
            ["git", "show", f"{commit}:{path}"], cwd=args.engine
        )
        tree = ast.parse(raw)
        functions = {
            node.name: hashlib.sha256(
                ast.dump(node, include_attributes=False).encode()
            ).hexdigest()
            for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef)
        }
        assert len(functions) == sum(
            isinstance(node, ast.FunctionDef) for node in ast.walk(tree)
        )
        files.append(
            {
                "path": path,
                "present": True,
                "sha256": hashlib.sha256(raw).hexdigest(),
                "function_ast_sha256": functions,
            }
        )
    rows.append(
        {
            "commit": commit,
            "author_date": metadata[0],
            "committer_date": metadata[1],
            "subject": metadata[2],
            "files": files,
        }
    )
summary = []
for path in paths:
    present = [
        (r["commit"], f)
        for r in rows
        for f in r["files"]
        if f["path"] == path and f["present"]
    ]
    assert present
    summary.append(
        {
            "path": path,
            "first_available_commit": present[0][0],
            "snapshots": len(present),
            "distinct_file_sha256": sorted({f["sha256"] for _, f in present}),
            "all_function_asts_match_selected": all(
                f["function_ast_sha256"] == present[-1][1]["function_ast_sha256"]
                for _, f in present
            ),
        }
    )
report = {
    "selected_revision": revision,
    "ancestor_commits": len(commits),
    "paths": summary,
    "snapshots": rows,
    "scope": "Complete reachable ancestry through the selected model revision for four named model files. Does not authenticate an unpublished working tree, loaded library/runtime, historical random state, or absent branches. No simulation or paper-completion verdict.",
}
args.output.write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps({"ancestor_commits": len(commits), "paths": summary}, indent=2))
