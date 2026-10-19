"""Audit full original-engine population-export qualification and sequential parity."""

import argparse
import csv
import hashlib
import json
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("run", type=Path)
parser.add_argument("reference", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
root = args.run
manifest = json.loads((root / "prepared/observer-manifest.json").read_text())
assert manifest["revision"] == "f5851488bf2369e2bbdc3f2499ed69c142de9fec"
pins = json.loads(
    (Path(__file__).parent / "timing/revision-fidelity.json").read_text()
)["hashes"]["timing"]
assert manifest["source_sha256"] == pins
for name, digest in pins.items():
    if name in manifest["changes"]:
        assert manifest["changes"][name]["original_sha256"] == digest
        digest = manifest["changes"][name]["exporter_sha256"]
    assert hashlib.sha256((root / "prepared" / name).read_bytes()).hexdigest() == digest
for name, digest in manifest["packaging_sha256"].items():
    assert hashlib.sha256((root / "prepared" / name).read_bytes()).hexdigest() == digest
qualification = root / "qualification"
assert (qualification / "exit-code.txt").read_text() == "0\n"
with args.reference.open() as stream:
    reference = list(csv.DictReader(stream))
assert len(reference) == 1000
reference_values = [(float(row["T"]), int(row["PopSize"])) for row in reference]
assert [row[0] for row in reference_values] == list(range(1000))
records = []
for variant in ["seq", "io", "tvar", "tarray"]:
    assert (qualification / f"{variant}-compiler.txt").read_text().strip() == "8.4.3"
    binary_digest, binary_path = (
        (qualification / f"{variant}-binary.sha256").read_text().split()
    )
    assert binary_path.startswith("/work/")
    assert (
        hashlib.sha256(
            (root / binary_path.removeprefix("/work/")).read_bytes()
        ).hexdigest()
        == binary_digest
    )
    for repetition in [1, 2]:
        path = qualification / f"{variant}-normal-{repetition}.csv"
        assert (path.with_suffix(".stderr")).read_bytes() == b""
        with path.open() as stream:
            reader = csv.DictReader(stream)
            assert reader.fieldnames == ["T", "PopSize"]
            rows = list(reader)
        times = [float(row["T"]) for row in rows]
        population = [int(row["PopSize"]) for row in rows]
        assert times == list(range(1000))
        assert all(0 <= count <= 500 for count in population)
        assert all(a >= b for a, b in zip(population[:-1], population[1:], strict=True))
        if variant == "seq":
            assert list(zip(times, population, strict=True)) == reference_values
        records.append(
            {
                "variant": variant,
                "repetition": repetition,
                "observations": len(rows),
                "first": population[0],
                "last": population[-1],
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "sequential_reference_parity": variant == "seq",
            }
        )
report = {
    "reference_sha256": hashlib.sha256(args.reference.read_bytes()).hexdigest(),
    "source_files_verified": len(pins),
    "runs": records,
    "observations": sum(row["observations"] for row in records),
    "scope": "Eight full1000-step runs at one capability, seed42,500agents,no rebirth. Local Linux amd64 emulation qualification only, not native-hardware timing or full concurrent-dynamics equivalence. Sequential output must equal the published unmodified-exporter reference; concurrent differences are retained without an equivalence verdict.",
}
args.output.mkdir(exist_ok=False)
(args.output / "audit.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report))
