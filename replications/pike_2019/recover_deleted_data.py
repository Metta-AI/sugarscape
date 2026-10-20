"""Recover twelve deleted author datasets without executing pickle constructors."""

import argparse
import csv
import hashlib
import json
from pathlib import Path
import pickletools
import statistics
import subprocess

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("engine", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
commit = "26df7d9cbcd75bb8f87b860a593dbd626af0d25e"
deleted = "de1882e66f58c578fe2908fe354e209332379f02"
selected = "585e53398f4f58e89ec184c83bb20819f0e4c96a"
tree = subprocess.check_output(
    ["git", "ls-tree", "-r", "-l", commit], cwd=args.engine, text=True
)
args.output.mkdir(exist_ok=False)
files = []
summaries = []
counts = []
for line in tree.splitlines():
    metadata, path = line.split("\t", 1)
    if not path.endswith(".p") or not path.startswith(
        ("Policy Network/", "Policy-Explicit/")
    ):
        continue
    _, kind, blob, size = metadata.split()
    assert kind == "blob" and int(size) < 40000000
    raw = subprocess.check_output(["git", "cat-file", "blob", blob], cwd=args.engine)
    assert len(raw) == int(size)
    assert (
        hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
        == blob
    )
    assert not subprocess.check_output(
        ["git", "ls-tree", "-r", deleted, "--", path], cwd=args.engine
    )
    destination = args.output / "raw" / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(raw)
    files.append(
        {
            "path": path,
            "git_blob": blob,
            "bytes": len(raw),
            "sha256": hashlib.sha256(raw).hexdigest(),
        }
    )
    if "sur_" in path:
        operations = list(pickletools.genops(raw))
        assert [op.name for op, _, _ in operations[:4]] == [
            "PROTO",
            "EMPTY_LIST",
            "BINPUT",
            "MARK",
        ]
        assert [op.name for op, _, _ in operations[-2:]] == ["APPENDS", "STOP"]
        assert all(op.name == "BININT1" for op, _, _ in operations[4:-2])
        values = [value for _, value, _ in operations[4:-2]]
        assert len(values) == 100 and all(0 <= value <= 200 for value in values)
        counts.extend((path, index, value) for index, value in enumerate(values))
        summaries.append(
            {
                "file": path,
                "runs": len(values),
                "mean": statistics.mean(values),
                "sample_sd": statistics.stdev(values),
                "minimum": min(values),
                "maximum": max(values),
            }
        )
assert len(files) == 12 and len(counts) == 300
cached = []
for revision, folder in [
    (commit, "Analysis Code"),
    (selected, "Results Analysis Code"),
]:
    for name in ["Data Analysis-Groups.ipynb", "Data Analysis-Groups-Policy.ipynb"]:
        path = f"{folder}/{name}"
        raw = subprocess.check_output(
            ["git", "show", f"{revision}:{path}"], cwd=args.engine
        )
        notebook = json.loads(raw)
        cell = notebook["cells"][19]
        assert "stats.ttest_ind" in "".join(cell["source"])
        outputs = [
            "".join(output["text"]) for output in cell["outputs"] if "text" in output
        ]
        assert len(outputs) == 1
        cached.append(
            {
                "revision": revision,
                "path": path,
                "sha256": hashlib.sha256(raw).hexdigest(),
                "cell_index": 19,
                "cached_text": outputs[0],
            }
        )
report = {
    "data_commit": commit,
    "deletion_commit": deleted,
    "selected_revision": selected,
    "files": files,
    "total_bytes": sum(row["bytes"] for row in files),
    "survivor_summaries": summaries,
    "notebook_comparison": cached,
    "scope": "Deleted pre-rerun author data. Three survivor arrays decoded from primitive opcodes; timing, price and metadata blobs recovered but not scientifically audited. Cached analyses changed after this snapshot; these data are not asserted to be the final published experiments. No new native runs or completed-paper credit.",
}
(args.output / "recovery.json").write_text(json.dumps(report, indent=2) + "\n")
with (args.output / "survivors.csv").open("x", newline="") as stream:
    writer = csv.writer(stream, lineterminator="\n")
    writer.writerow(["file", "run", "survivors"])
    writer.writerows(counts)
print(
    json.dumps(
        {
            "files": len(files),
            "bytes": report["total_bytes"],
            "survivor_summaries": summaries,
        }
    )
)
