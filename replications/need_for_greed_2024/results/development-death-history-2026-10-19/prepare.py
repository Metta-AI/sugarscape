from pathlib import Path
import subprocess
import json
import hashlib
import ast

root = Path(__file__).resolve().parent
repo = Path("/Users/relh/Code/workspace/sugarscape-replications")
head = subprocess.check_output(
    ["git", "-C", str(repo), "rev-parse", "upstream/master"], text=True
).strip()
commits = subprocess.check_output(
    [
        "git",
        "-C",
        str(repo),
        "log",
        head,
        "--since=2024-01-01",
        "--until=2025-01-01",
        "--format=%H",
        "--",
        "plots/plot.py",
    ],
    text=True,
).splitlines()
rows = []
for commit in commits:
    source = subprocess.check_output(
        ["git", "-C", str(repo), "show", commit + ":plots/plot.py"]
    )
    tree = ast.parse(source)
    assignments = [
        ast.unparse(n.value)
        for n in ast.walk(tree)
        if isinstance(n, ast.Assign)
        and any(isinstance(t, ast.Name) and t.id == "deaths" for t in n.targets)
    ]
    row = {
        "commit": commit,
        "author_date": subprocess.check_output(
            ["git", "-C", str(repo), "show", "-s", "--format=%aI", commit], text=True
        ).strip(),
        "source_sha256": hashlib.sha256(source).hexdigest(),
        "deaths_assignments": assignments,
        "median_calls": [
            ast.unparse(n.func)
            for n in ast.walk(tree)
            if isinstance(n, ast.Call) and "median" in ast.unparse(n.func).lower()
        ],
    }
    rows.append(row)
    (root / (commit[:8] + "-plot.py")).write_bytes(source)
intro = "31cb37cd5c61aa5dbd121a025bc1986423822b78"
first = next(r for r in rows if r["commit"] == intro)
assert (
    len(first["deaths_assignments"]) == 1
    and "agentAgingDeaths" in first["deaths_assignments"][0]
)
parent = subprocess.check_output(
    ["git", "-C", str(repo), "show", intro + "^:plots/plot.py"]
)
assert b"agentAgingDeaths" not in parent
(root / "pre-introduction-plot.py").write_bytes(parent)
(root / "history.json").write_text(
    json.dumps(
        {
            "repository": "https://github.com/nkremerh/sugarscape",
            "checked_head": head,
            "scope": "Commits touching plots/plot.py on upstream master selected by Git calendar2024 date filter. Dates are repository metadata, not proof of paper production time. Absence of median calls in this file does not exclude external plotting scripts.",
            "commits": rows,
            "introduction": intro,
            "parent_source_sha256": hashlib.sha256(parent).hexdigest(),
        },
        indent=2,
    )
    + "\n"
)
source = (root / (intro[:8] + "-plot.py")).read_bytes()
(root / "author-plot.py").write_bytes(source)
(root / "source.json").write_text(
    json.dumps(
        {
            "repository": "https://github.com/nkremerh/sugarscape",
            "commit": intro,
            "path": "plots/plot.py",
            "sha256": hashlib.sha256(source).hexdigest(),
            "scope": "First aging-inclusive findMeans in inspected development history; June30,2024 Git author date. Not proven paper plotting source.",
        },
        indent=2,
    )
    + "\n"
)
(root / "LICENSE.author").write_bytes(
    subprocess.check_output(["git", "-C", str(repo), "show", intro + ":LICENSE"])
)
old = root.parent / "need-for-greed-author-plot-control-001/analyze.py"
(root / "analyze.py").write_text(
    old.read_text()
    .replace("later author plotting function", "June 2024 author plotting function")
    .replace(
        "Unmodified v2024.3 author findMeans", "Unmodified June30,2024 author findMeans"
    )
)
print(
    "Historical snapshots",
    len(rows),
    "aging-inclusive",
    sum(bool(r["deaths_assignments"]) for r in rows),
)
