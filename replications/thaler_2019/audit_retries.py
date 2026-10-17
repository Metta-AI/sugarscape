"""Audit complete instrumented native workflows and cumulative STM counters."""

import argparse
import hashlib
import json
from pathlib import Path
import re

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("run", type=Path)
parser.add_argument("original_source", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
assert not args.output.exists()
protocol = json.loads((args.run / "protocol.json").read_text())
assert json.loads((args.run / "complete.json").read_text()) == {
    "completed_processes": 2
}
assert (
    protocol["seed"],
    protocol["steps"],
    protocol["population"],
    protocol["rebirthing"],
    protocol["capabilities"],
    protocol["iterations_per_process"],
) == (42, 1000, 500, False, 1, 2)
for name, digest in protocol["source_sha256"].items():
    assert (
        hashlib.sha256((args.original_source / name).read_bytes()).hexdigest() == digest
    )
for name, digest in json.loads(
    (args.run / "auxiliary-source-sha256.json").read_text()
).items():
    assert hashlib.sha256((args.run / name).read_bytes()).hexdigest() == digest
results = []
for variant in ["tvar", "tarray"]:
    prefix = f"criterion/sugarscape-{variant}/"
    for name, digest in protocol["source_sha256"].items():
        if name.startswith(prefix):
            relative = Path(name).relative_to(prefix)
            original = (args.original_source / name).read_bytes()
            measured = (args.run / variant / relative).read_bytes()
            if str(relative) == "src/Main.hs":
                needle = b"\n      let stmStatsFlag = False  -- collects STM statistics. WARNING: reduces performance!"
                assert original.count(needle) == 1
                assert measured == original.replace(
                    needle, needle.replace(b"False", b"True "), 1
                )
                assert (
                    hashlib.sha256(measured).hexdigest()
                    == protocol["changes"][variant]["instrumented_sha256"]
                )
            else:
                assert measured == original
    folder = args.run / "recovered-runs" / variant
    command = json.loads((folder / "command.json").read_text())
    assert command["compiler"] == "8.4.3"
    executable = args.run / Path(command["command"][0]).relative_to(
        "/root/sugarscape/thaler-retries-002"
    )
    assert (
        hashlib.sha256(executable.read_bytes()).hexdigest() == command["binary_sha256"]
    )
    assert command["command"][1:] == [
        "--iters",
        "2",
        "--match",
        "prefix",
        f"sugarscape-{variant}-normal:1/500",
        "+RTS",
        "-N1",
        "-RTS",
    ]
    assert json.loads((folder / "exit.json").read_text())["exit_code"] == 0
    assert (folder / "stdout.log").read_text().strip() == f"benchmarking sugarscape-{variant}-normal:1/500"
    log = (folder / "stderr.log").read_text()
    counters = re.findall(
        r"^SugarScape\s+(\d+)\s+(\d+)\s+(\d+\.\d+)\s*$", log, re.MULTILINE
    )
    assert len(counters) == log.count("STM transaction statistics (") == 2
    previous_commits = previous_retries = 0
    iterations = []
    for index, (commits, retries, printed) in enumerate(counters, 1):
        commits, retries = int(commits), int(retries)
        assert commits > previous_commits and retries >= previous_retries
        ratio = retries / commits
        assert f"{ratio:.2f}" == printed
        delta_commits, delta_retries = (
            commits - previous_commits,
            retries - previous_retries,
        )
        iterations.append(
            {
                "iteration": index,
                "cumulative_commits": commits,
                "cumulative_retries": retries,
                "cumulative_ratio": ratio,
                "printed_ratio": printed,
                "iteration_commits": delta_commits,
                "iteration_retries": delta_retries,
                "iteration_ratio": delta_retries / delta_commits,
                "printed_zero_with_nonzero_retries": printed == "0.00" and retries > 0,
            }
        )
        previous_commits, previous_retries = commits, retries
    results.append(
        {
            "variant": variant,
            "binary_sha256": command["binary_sha256"],
            "iterations": iterations,
            "files_sha256": {
                f.name: hashlib.sha256(f.read_bytes()).hexdigest()
                for f in sorted(folder.iterdir())
                if f.is_file()
            },
        }
    )
report = {
    "protocol_sha256": hashlib.sha256(
        (args.run / "protocol.json").read_bytes()
    ).hexdigest(),
    "completed_processes": 2,
    "completed_model_iterations": 4,
    "results": results,
    "scope": "Instrumented 1000-step native workflows under emulation, one Haskell capability. Counters cover the author's SugarScape label; ratios are retries/commits. Not a hardware timing or full retry-table replication.",
}
args.output.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
print(json.dumps(report))
