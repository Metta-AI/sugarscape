from pathlib import Path
import concurrent.futures
import hashlib
import json
import subprocess
import tarfile

root = Path(__file__).resolve().parent
base = root.parent
archive = root / "checkpoint.tar.gz"
expected = json.loads((root / "export.json").read_text())
assert hashlib.sha256(archive.read_bytes()).hexdigest() == expected["sha256"]
download = root / "download"
download.mkdir()
with tarfile.open(archive) as bundle:
    bundle.extractall(download, filter="data")
checkpoint = json.loads((download / "checkpoint.json").read_text())
assert checkpoint["completed"] == expected["completed"]
assert {row["phase"] for row in checkpoint["segments"]} == {2,3}
python = base.parent / "sugarscape-replications/.venv/bin/python"
script = base.parent / "sugarscape-pike/replications/pike_2019/reconcile_segments.py"
commands = []
for phase,original,old_count in [(2,"pike-phase2-001",61),(3,"pike-phase3-movement-001",29)]:
    original = base / original
    local = base / f"pike-segment-phase{phase}-003"
    command = [str(python),str(script),str(phase),str(root/f"reconciled-phase{phase}"),"--segment",str(original),"0",str(original),"--segment",str(local),str(old_count),str(local)]
    for segment in checkpoint["segments"]:
        if segment["phase"] == phase:
            command.extend(["--segment",str(download/segment["snapshot"]),str(segment["start"]),segment["recorded_root"]])
    commands.append(command)
(root/"commands.json").write_text(json.dumps(commands,indent=2)+"\n")
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
    results = list(pool.map(lambda command:subprocess.run(command,capture_output=True,text=True),commands))
for phase,result in zip([2,3],results,strict=True):
    (root/f"phase{phase}.log").write_text(result.stdout+result.stderr)
    assert result.returncode == 0,(phase,result.stderr)
reports = [json.loads((root/f"reconciled-phase{phase}/reconciliation.json").read_text()) for phase in [2,3]]
summary = {"archive_sha256":expected["sha256"],"cloud_conditions":checkpoint["completed"],"total_phase2_and_phase3_conditions":sum(r["validated_runs"] for r in reports),"phase_counts":{str(r["phase"]):r["validated_runs"] for r in reports},"health_records":sum(r["health_records"] for r in reports),"price_step_records":sum(r["price_step_records"] for r in reports),"scope":"Full completed-prefix raw-output audit of PhaseII/III only; includes earlier prefixes without double-counting. PhaseI300 already separately audited. No new whole-paper completion."}
assert summary["total_phase2_and_phase3_conditions"] == 92+checkpoint["completed"]
(root/"validation.json").write_text(json.dumps(summary,indent=2)+"\n")
print(json.dumps(summary))
