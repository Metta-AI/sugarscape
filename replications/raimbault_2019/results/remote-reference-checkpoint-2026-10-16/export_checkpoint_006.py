from pathlib import Path
import json
import hashlib
import tarfile

root = Path("/root/sugarscape/reference-queue-001")
chunks = []
for p in sorted(root.glob("rows-*/audit/audit.json")):
    a = json.loads(p.read_text())
    assert (
        a["mode"] == "complete"
        and a["mismatch_count"] == 0
        and a["compared_measurements"] == 2 * a["rows"]
    )
    chunks.append(p.parent.parent)
output = Path("/root/sugarscape/reference-checkpoint-006.tar.gz")
assert not output.exists()
with tarfile.open(output, "w:gz") as t:
    for name in ["plan.json", "start.json"]:
        t.add(root / name, arcname=name)
    for p in chunks:
        t.add(p, arcname=p.name)
report = {
    "archive": str(output),
    "bytes": output.stat().st_size,
    "sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
    "chunks": len(chunks),
    "scope": "Sealed completed chunks only; native queue continues unchanged.",
}
print(json.dumps(report), flush=True)
