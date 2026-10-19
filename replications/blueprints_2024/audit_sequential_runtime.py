"""Compare sequential runtime controls with retained original-input trajectories."""

import argparse
import hashlib
import json
from pathlib import Path
import re
import statistics
import tarfile

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("archive", type=Path)
parser.add_argument("reference", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
reports = []
with tarfile.open(args.archive) as current, tarfile.open(args.reference) as reference:
    protocol = json.load(current.extractfile("protocol.json"))
    complete = json.load(current.extractfile("complete.json"))
    ledger = [json.loads(line) for line in current.extractfile("completed.jsonl")]
    assert ledger == complete["runs"] and len(ledger) == 8
    assert protocol["source_revision"] == "b9ca671ab7591c7b3606f2d76c33eda344d626d1"
    assert protocol["order"] == ["cpython", "pypy", "pypy", "cpython"]
    assert complete["versions"]["cpython"] == "Python 3.11.14"
    assert (
        "Python 3.11.13" in complete["versions"]["pypy"]
        and "PyPy 7.3.20" in complete["versions"]["pypy"]
    )
    assert (
        protocol["runtime_sha256"]
        == "1410db3a7ae47603e2b7cbfd7ff6390b891b2e041c9eb4f1599f333677bccb3e"
    )
    assert len(protocol["conditions"]) == 2
    expected_keys = []
    for condition in protocol["conditions"]:
        entry = condition["entry"]
        name = entry.removesuffix(".config")
        prior = "runs/" + name
        original = current.extractfile(entry).read()
        assert hashlib.sha256(original).hexdigest() == condition["configuration_sha256"]
        assert original == reference.extractfile(prior + "/original.config").read()
        original_config = json.loads(original)
        reference_config = json.load(reference.extractfile(prior + "/config.json"))
        reference_manifest = json.load(reference.extractfile(prior + "/manifest.json"))
        assert reference_manifest["source_sha256"] == protocol["source_sha256"]
        assert reference_manifest["release"] == protocol["source_revision"]
        expected = reference.extractfile(prior + "/trajectory.json").read()
        assert (
            hashlib.sha256(expected).hexdigest()
            == condition["expected_trajectory_sha256"]
        )
        for order, runtime in enumerate(protocol["order"]):
            expected_keys.append((entry, runtime, order))
            row = ledger[len(expected_keys) - 1]
            assert (row["entry"], row["runtime"], row["order"]) == expected_keys[-1]
            prefix = "runs/" + name + "-" + str(order) + "-" + runtime
            config = json.load(current.extractfile(prefix + "/config.json"))
            assert config == reference_config | {"logfile": config["logfile"]}
            assert config == original_config | {"logfile": config["logfile"]}
            assert (
                json.load(current.extractfile(prefix + "/exit.json"))["exit_code"] == 0
            )
            trajectory = current.extractfile(prefix + "/trajectory.json").read()
            assert trajectory == expected
            assert hashlib.sha256(trajectory).hexdigest() == row["trajectory_sha256"]
            records = json.loads(trajectory)
            assert len(records) == row["observations"] == 5001
            assert [record["timestep"] for record in records] == list(range(5001))
            assert records[-1]["population"] == row["final_population"]
            assert row["elapsed_seconds"] > 0
            command = json.load(current.extractfile(prefix + "/command.json"))
            assert command[:3] == ["/usr/bin/time", "-v", "-o"]
            assert command[-2:] == [
                "--conf",
                config["logfile"].replace("trajectory.json", "config.json"),
            ]
            assert f"/{runtime}/" in command[4]
            memory = current.extractfile(prefix + "/memory.log").read().decode()
            assert re.search(r"Exit status:\s*0\s*$", memory)
            rss = int(
                re.search(
                    r"Maximum resident set size \(kbytes\):\s*(\d+)", memory
                ).group(1)
            )
            assert rss > 0
            reports.append(
                {**row, "maximum_rss_kib": rss, "byte_exact_to_original_control": True}
            )
    assert len(set(expected_keys)) == 8
    groups = []
    for condition in protocol["conditions"]:
        selected = [row for row in reports if row["entry"] == condition["entry"]]
        means = {
            runtime: statistics.mean(
                row["elapsed_seconds"] for row in selected if row["runtime"] == runtime
            )
            for runtime in ["cpython", "pypy"]
        }
        groups.append(
            {
                "entry": condition["entry"],
                "runs_per_runtime": 2,
                "mean_seconds": means,
                "mean_speedup_ratio": means["cpython"] / means["pypy"],
                "rss_kib_ranges": {
                    runtime: [
                        min(
                            row["maximum_rss_kib"]
                            for row in selected
                            if row["runtime"] == runtime
                        ),
                        max(
                            row["maximum_rss_kib"]
                            for row in selected
                            if row["runtime"] == runtime
                        ),
                    ]
                    for runtime in ["cpython", "pypy"]
                },
            }
        )
report = {
    "complete_runs": 8,
    "byte_exact_trajectories": 8,
    "observations": 40008,
    "independent_scientific_inputs_added": 0,
    "versions": complete["versions"],
    "groups": groups,
    "runs": reports,
    "archive_sha256": hashlib.sha256(args.archive.read_bytes()).hexdigest(),
    "reference_archive_sha256": hashlib.sha256(args.reference.read_bytes()).hexdigest(),
    "scope": "Sequential timing/memory controls on one two-CPU allocation, two repeats per runtime and two configurations at one seed. Exact recorded trajectories do not establish universal runtime equivalence. Timings are not historical-paper performance. These repeated inputs add no supplementary configurations or paper completion.",
}
with args.output.open("x") as stream:
    stream.write(json.dumps(report, indent=2) + "\n")
print(json.dumps({key: value for key, value in report.items() if key not in ["runs"]}))
