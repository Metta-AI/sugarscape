"""Replay all completed searches and verify an immutable full native archive."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import sys
import tarfile

root = Path(__file__).resolve().parent
campaign = root.parent / "oremland-frontier-transfer-001"
plan = json.loads((campaign / "plan.json").read_bytes())
terminal = json.loads((campaign / "terminal.json").read_bytes())
assert terminal["all_complete"] and terminal["planned"] == 18
assert terminal["completed"] == [job["name"] for job in plan["jobs"]]
assert sum(job["native_runs"] for job in plan["jobs"]) == 432000
assert hashlib.sha256((campaign / "audit_optimizer.py").read_bytes()).hexdigest() == plan["auditor_sha256"]
assert shutil.disk_usage(root).free > 3 * 1024**3
(root / "audits").mkdir()
rows = []
files = {}
for job in plan["jobs"]:
    folder = campaign / job["name"]
    assert json.loads((folder / "terminal.json").read_bytes())["exit_code"] == 0
    output = root / "audits" / (job["name"] + ".json")
    process = subprocess.run([sys.executable, str(campaign / "audit_optimizer.py"), str(folder / "run"), str(output)], capture_output=True, text=True, timeout=180)
    (root / "audits" / (job["name"] + ".receipt.json")).write_text(json.dumps({"exit_code": process.returncode, "stdout": process.stdout, "stderr": process.stderr}, indent=2) + "\n")
    assert process.returncode == 0, process.stderr
    assert output.read_bytes() == (folder / "audit.json").read_bytes()
    audit = json.loads(output.read_bytes())
    assert audit["native_runs"] == 24000 and audit["evaluated_generations"] == 20
    rows.append({"name": job["name"], "width": job["width"], "optimizer_seed": job["optimizer_seed"], **{k: v for k, v in audit.items() if k not in ["sha256", "scope"]}})
    for path in sorted(folder.rglob("*")):
        assert not path.is_symlink()
        if path.is_file():
            files[str(path.relative_to(campaign))] = hashlib.sha256(path.read_bytes()).hexdigest()
    print(json.dumps({"replayed": job["name"], "native_runs": audit["native_runs"]}), flush=True)
for name in ["plan.json", "terminal.json", "run_frontier_campaign.py", "run_optimizer.py", "audit_optimizer.py"]:
    files[name] = hashlib.sha256((campaign / name).read_bytes()).hexdigest()
for path in sorted((campaign / "models").rglob("*")):
    assert not path.is_symlink()
    if path.is_file():
        files[str(path.relative_to(campaign))] = hashlib.sha256(path.read_bytes()).hexdigest()
archive = root / "complete-searches.tar.gz"
with tarfile.open(archive, "x:gz") as bundle:
    for name, digest in files.items():
        path = campaign / name
        assert hashlib.sha256(path.read_bytes()).hexdigest() == digest
        bundle.add(path, arcname=name, recursive=False)
with tarfile.open(archive) as bundle:
    members = bundle.getmembers()
    assert all(m.isfile() and not Path(m.name).is_absolute() and ".." not in Path(m.name).parts for m in members)
    assert len({m.name for m in members}) == len(members) == len(files)
    actual = {m.name: hashlib.sha256(bundle.extractfile(m).read()).hexdigest() for m in members}
assert actual == files
report = {
    "searches": len(rows), "native_runs": sum(r["native_runs"] for r in rows),
    "evaluated_generations": sum(r["evaluated_generations"] for r in rows),
    "matings_replayed": sum(r["matings"] for r in rows),
    "mutated_components_replayed": sum(r["mutated_components"] for r in rows),
    "final_frontier_policies": sum(r["final_frontier_size"] for r in rows),
    "all_repeated_audits_byte_identical": True,
    "groups": rows, "archive_bytes": archive.stat().st_size,
    "archive_sha256": hashlib.sha256(archive.read_bytes()).hexdigest(),
    "archive_members_verified": len(files), "member_sha256": files,
    "scope": "All eighteen frozen optimizer workflows complete and replay exactly. Native archive readback verified. Held-out transfers, timing benchmark and final paper synthesis remain separate; no global-optimality claim.",
}
(root / "audit.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps({k: v for k, v in report.items() if k not in ["groups", "member_sha256"]}), flush=True)
