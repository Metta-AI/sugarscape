"""Execute disjoint remaining conditions after auditing the first continuation."""

import concurrent.futures
import hashlib
import json
import subprocess
import sys
import tarfile
import time
from pathlib import Path

root = Path("/root/sugarscape/pike-common-five-continuation-001")
base = root.parent
first = json.loads((root / "first-002-audit/audit.json").read_text())
assert first["ordinal_interval"] == [119, 120]
assert first["structurally_audited_runs"] == 1
ranges = [(i, i + 10) for i in range(120, 200, 10)]
assert len(ranges) == 8
(root / "remaining-plan.json").write_text(
    json.dumps({"intervals": ranges, "workers": 8, "per_condition_timeout": 240, "outer_limit_seconds": 3600}) + "\n"
)
started = time.monotonic()


def execute(interval):
    start, stop = interval
    output = root / f"rows-{start}-{stop}"
    command = [
        sys.executable,
        str(root / "run_common_five.py"),
        str(base / "pike-portability-001/engine"),
        str(base / "pike-portability-001/library"),
        str(output),
        "--start-index",
        str(start),
        "--stop-index",
        str(stop),
    ]
    with (root / f"rows-{start}-{stop}.log").open("x") as log:
        result = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, timeout=2700)
    (root / f"rows-{start}-{stop}.exit.json").write_text(
        json.dumps({"exit_code": result.returncode, "command": command}) + "\n"
    )
    assert result.returncode == 0
    assert json.loads((output / "complete.json").read_text()) == {"completed_runs": 10}
    audit = [
        sys.executable,
        str(root / "audit_common_resources.py"),
        str(output),
        "prefix",
        str(root / f"rows-{start}-{stop}-audit"),
        "--threshold",
        "5",
        "--start-index",
        str(start),
    ]
    with (root / f"rows-{start}-{stop}-audit.log").open("x") as log:
        subprocess.run(audit, stdout=log, stderr=subprocess.STDOUT, check=True, timeout=300)
    return {"interval": interval, "runs": 10}


with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
    reports = list(pool.map(execute, ranges))
(root / "remaining-complete.json").write_text(
    json.dumps(
        {
            "intervals": reports,
            "completed_runs": 80,
            "elapsed_seconds": time.monotonic() - started,
            "scope": "Structural execution completion only. Native numerical failures remain retained.",
        },
        indent=2,
    )
    + "\n"
)
archive = base / "pike-common-five-continuation-001.tar.gz"
assert not archive.exists()
with tarfile.open(archive, "w:gz") as stream:
    stream.add(root, arcname=root.name)
with archive.open("rb") as stream:
    checksum = hashlib.file_digest(stream, "sha256").hexdigest()
print(json.dumps({"archive": str(archive), "bytes": archive.stat().st_size, "sha256": checksum}), flush=True)
