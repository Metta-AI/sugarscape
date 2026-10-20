"""Reaudit a sealed Table IV prefix against both original deposited archives."""

from pathlib import Path
import hashlib
import json
import subprocess
import sys
import tarfile
import zipfile

root = Path(__file__).resolve().parent
archive = root / "checkpoint-pilots.tar.gz"
assert archive.stat().st_size == 128876
assert (
    hashlib.sha256(archive.read_bytes()).hexdigest()
    == "5e14ee4448632fb456b7eb1edb4342ec9d95a734ec14a4204c03c827aad66c7d"
)
native = root / "native"
native.mkdir()
with tarfile.open(archive) as tar:
    members = tar.getmembers()
    assert len({m.name for m in members}) == len(members)
    assert all(m.isfile() or m.isdir() for m in members)
    assert all(
        not Path(m.name).is_absolute() and ".." not in Path(m.name).parts
        for m in members
    )
    hashes = {
        m.name: hashlib.sha256(tar.extractfile(m).read()).hexdigest()
        for m in members
        if m.isfile()
    }
    tar.extractall(native, filter="data")
for name, digest in hashes.items():
    assert hashlib.sha256((native / name).read_bytes()).hexdigest() == digest
qualified = root.parent / "need-for-greed-unassigned-runner-002/batch-00"
for name in (
    "protocol.json",
    "run_supplement_batch.py",
    "run_supplement.py",
    "audit_supplement.py",
    "source-sha256.json",
    "bootstrap.sh",
):
    assert (native / name).read_bytes() == (qualified / name).read_bytes()
original_archive = root.parent / "papers/need-for-greed.zip"
assert (
    hashlib.sha256(original_archive.read_bytes()).hexdigest()
    == "e41c89ed31811b2d100c0a54f9c0110f0572a980b599e2417b2653b934fbe440"
)
reports = []
commands = []
with zipfile.ZipFile(original_archive) as original:
    for run in sorted((native / "runs").iterdir()):
        manifest = json.loads((run / "manifest.json").read_bytes())
        assert (run / "original.config").read_bytes() == original.read(
            manifest["entry"]
        )
        receipt = json.loads((native / "logs" / (run.name + ".exit.json")).read_bytes())
        assert receipt["exit_code"] == 0
        cmd = [
            sys.executable,
            str(native / "audit_supplement.py"),
            str(root.parent / "papers/blueprints-selfishness.zip"),
            str(run),
            str(root / "audits" / run.name),
            "--expected-runtime",
            run.name.rsplit("-", 1)[1],
        ]
        process = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        commands.append(
            {
                "command": cmd,
                "exit_code": process.returncode,
                "stdout": process.stdout,
                "stderr": process.stderr,
            }
        )
        (root / "audit-commands.json").write_text(json.dumps(commands, indent=2) + "\n")
        assert process.returncode == 0, process.stderr
        reports.append(json.loads(process.stdout))
assert len(reports) == 4 and len({r["entry"] for r in reports}) == 2
for entry in {r["entry"] for r in reports}:
    stem = entry.removesuffix(".config")
    assert (native / "runs" / (stem + "-cpython") / "trajectory.json").read_bytes() == (
        native / "runs" / (stem + "-pypy") / "trajectory.json"
    ).read_bytes()
assert all(
    len({json.dumps(r, sort_keys=True) for r in reports if r["entry"] == entry}) == 1
    for entry in {r["entry"] for r in reports}
)
reports = list({r["entry"]: r for r in reports}.values())
result = {
    "archive_sha256": hashlib.sha256(archive.read_bytes()).hexdigest(),
    "archive_bytes": archive.stat().st_size,
    "member_sha256": hashes,
    "inputs": len(reports),
    "observations": sum(r["observations"] for r in reports),
    "runs": reports,
    "paper_configurations_byte_exact": True,
    "qualified_payload_bytes_exact": True,
    "scope": "Fresh raw audit of two full CPython/PyPy pilot pairs. Unique inputs count once; coverage reconciliation required.",
}
(root / "audit.json").write_text(json.dumps(result, indent=2) + "\n")
print(
    json.dumps({k: v for k, v in result.items() if k not in ("runs", "member_sha256")})
)
