"""Run a bounded comparison of single-iteration and original Criterion retry collection."""

import argparse
import hashlib
import json
from pathlib import Path
import random
import re
import subprocess
import time

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("binary", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
assert (
    hashlib.sha256(args.binary.read_bytes()).hexdigest()
    == "41574620bf9fbf82c58c7bf1e0774c4554215236b837971053d1a9244039013e"
)
args.output.mkdir()
schedule = [
    (mode, repetition)
    for mode in ["single", "criterion_default"]
    for repetition in range(3)
]
random.Random(20261018).shuffle(schedule)
(args.output / "schedule.json").write_text(json.dumps(schedule, indent=2) + "\n")
with (args.output / "completed.jsonl").open("x") as ledger:
    for index, (mode, repetition) in enumerate(schedule):
        folder = args.output / f"{index:02d}-{mode}-{repetition}"
        folder.mkdir()
        command = [
            str(args.binary.resolve()),
            "--match",
            "prefix",
            "sugarscape-tarray-normal:32/500",
        ]
        command += (
            ["--iters", "1"]
            if mode == "single"
            else ["--output", str((folder / "criterion.html").resolve())]
        )
        command += ["+RTS", "-N32", "-RTS"]
        (folder / "command.json").write_text(json.dumps(command, indent=2) + "\n")
        started = time.monotonic()
        with (
            (folder / "stdout.log").open("w") as stdout,
            (folder / "stderr.log").open("w") as stderr,
        ):
            result = subprocess.run(command, stdout=stdout, stderr=stderr, timeout=540)
        (folder / "exit-code.txt").write_text(str(result.returncode) + "\n")
        result.check_returncode()
        text = (folder / "stderr.log").read_text()
        counters = re.findall(
            r"^SugarScape\s+(\d+)\s+(\d+)\s+(\d+\.\d+)\s*$", text, re.MULTILINE
        )
        assert len(counters) == text.count("STM transaction statistics (")
        assert len(counters) == 1 if mode == "single" else len(counters) >= 2
        observations = []
        prior_commits = prior_retries = 0
        for commits_text, retries_text, printed in counters:
            commits, retries = int(commits_text), int(retries_text)
            assert commits > prior_commits and retries >= prior_retries
            assert f"{retries / commits:.2f}" == printed
            observations.append(
                {
                    "cumulative_commits": commits,
                    "cumulative_retries": retries,
                    "cumulative_ratio": retries / commits,
                    "printed_ratio": printed,
                    "increment_commits": commits - prior_commits,
                    "increment_retries": retries - prior_retries,
                    "increment_ratio": (retries - prior_retries)
                    / (commits - prior_commits),
                }
            )
            prior_commits, prior_retries = commits, retries
        record = {
            "index": index,
            "mode": mode,
            "repetition": repetition,
            "exit_code": result.returncode,
            "elapsed_seconds": time.monotonic() - started,
            "observations": observations,
            "files_sha256": {
                p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                for p in folder.iterdir()
            },
        }
        ledger.write(json.dumps(record) + "\n")
        ledger.flush()
        print(
            json.dumps(
                {
                    "index": index,
                    "mode": mode,
                    "completed_simulations": len(observations),
                    "final_ratio": observations[-1]["cumulative_ratio"],
                }
            ),
            flush=True,
        )
