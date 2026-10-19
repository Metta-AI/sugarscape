"""Audit sealed progress diagnostics against the qualified source and binaries."""

import argparse
import difflib
import hashlib
import json
from pathlib import Path
import tarfile

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("archive", type=Path)
parser.add_argument("receipt", type=Path)
parser.add_argument("qualification", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
receipt = json.loads(args.receipt.read_text())["receipt"]
assert hashlib.sha256(args.archive.read_bytes()).hexdigest() == receipt["sha256"]
assert args.archive.stat().st_size == receipt["bytes"]
with tarfile.open(args.qualification) as qualified:
    manifest = json.load(
        qualified.extractfile("qualification/native/effective-source-sha256.json")
    )
with tarfile.open(args.archive) as archive:
    files = {
        m.name: archive.extractfile(m).read()
        for m in archive.getmembers()
        if m.isfile()
    }
prefix = "diagnostic/native/"
changed = "dynasoar/example/sugarscape/dynasoar_no_cell/sugarscape.cu"
for name, digest in manifest.items():
    data = files[
        prefix + ("original-sugarscape.cu" if name == changed else "source/" + name)
    ]
    assert hashlib.sha256(data).hexdigest() == digest, name
before = files[prefix + "original-sugarscape.cu"].decode()
after = files[prefix + "source/" + changed].decode()
diff = list(difflib.unified_diff(before.splitlines(), after.splitlines(), lineterm=""))
observer_start = after.index("static int observed_iteration = -1;")
observer_end = after.index("void step() {", observer_start)
stripped = after[:observer_start] + after[observer_end:]
stripped_lines = [
    line.strip()
    for line in stripped.splitlines()
    if line.strip()
    and not line.strip().startswith('progress("')
    and line.strip() != "observed_iteration = i;"
]
assert stripped_lines == [line.strip() for line in before.splitlines() if line.strip()]
change = json.loads(files[prefix + "observer-change.json"])
assert change["original_sha256"] == hashlib.sha256(before.encode()).hexdigest()
assert change["observed_sha256"] == hashlib.sha256(after.encode()).hexdigest()
records = json.loads(files[prefix + "records.json"])
observations = []
for row in records:
    label = f"{row['mode']}-{row['grid_side']}"
    assert hashlib.sha256(files[prefix + label]).hexdigest() == row["binary_sha256"]
    stderr = files[prefix + label + ".stderr"].decode()
    progress = [line for line in stderr.splitlines() if line.startswith("PROGRESS ")]
    completed = [
        int(line.split()[1]) for line in progress if line.endswith(" step-complete")
    ]
    observations.append(
        {
            **row,
            "last_progress": progress[-1],
            "last_observed_completed_iteration": max(completed, default=-1),
            "active_mask_assertion": "Assertion `__activemask() == active` failed"
            in stderr,
        }
    )
    if row["returncode"] == 0:
        assert max(completed) == 9900
args.output.mkdir(parents=True, exist_ok=False)
(args.output / "audit.json").write_text(
    json.dumps(
        {
            "archive_sha256": receipt["sha256"],
            "qualified_source_files_checked": len(manifest),
            "original_statements_preserved_after_observer_removal": True,
            "terminal": json.loads(files["diagnostic/terminal.json"]),
            "observations": observations,
            "scope": "Binary/source integrity and observed progress only. No full-state validation, benchmark timing or negative paper verdict.",
        },
        indent=2,
    )
    + "\n"
)
(args.output / "observer.diff").write_text("\n".join(diff) + "\n")
for name, data in files.items():
    if (
        name
        in (
            "diagnostic/native.log",
            "diagnostic/terminal.json",
            "diagnostic/diagnose_progress.py",
        )
        or name.startswith(prefix)
        and (
            name.endswith((".stdout", ".stderr", "-build.log"))
            or name in (prefix + "records.json", prefix + "observer-change.json")
        )
    ):
        (args.output / Path(name).name).write_bytes(data)
