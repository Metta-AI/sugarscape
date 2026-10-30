"""Replay the original shared seed schedule and preserve lossless trajectories."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import zipfile

from run import ARCHIVE_SHA256, Configuration


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("engine", type=Path)
    parser.add_argument("archive", type=Path)
    parser.add_argument("model")
    parser.add_argument("output", type=Path)
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--stop", type=int, default=500)
    args = parser.parse_args()
    assert 0 <= args.start < args.stop <= 500
    assert hashlib.sha256(args.archive.read_bytes()).hexdigest() == ARCHIVE_SHA256
    with zipfile.ZipFile(args.archive) as archive:
        configs = [Configuration.model_validate_json(archive.read(name)) for name in archive.namelist()]
    models = sorted({c.agentDecisionModels[0] for c in configs})
    assert len(configs) == 2000 and len(models) == 4 and args.model in models
    schedules = {m: sorted(c.seed for c in configs if c.agentDecisionModels == [m]) for m in models}
    seeds = schedules[args.model]
    assert len(set(seeds)) == 500 and all(s == seeds for s in schedules.values())
    runner = Path(__file__).with_name("run.py").resolve()
    args.output.mkdir(parents=True, exist_ok=False)
    manifest = {"model": args.model, "seeds": seeds[args.start:args.stop], "start": args.start, "stop": args.stop,
                "archive_sha256": ARCHIVE_SHA256, "runner_sha256": hashlib.sha256(runner.read_bytes()).hexdigest(),
                "batch_runner_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                "scope": "Original author configuration archive; sorted original seeds, not newly sampled replacements."}
    (args.output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    with (args.output / "completed.jsonl").open("x") as completed:
        for seed in manifest["seeds"]:
            assert hashlib.sha256(runner.read_bytes()).hexdigest() == manifest["runner_sha256"]
            assert shutil.disk_usage(args.output).free >= 1024**3
            output = args.output / f"seed-{seed}"
            command = [sys.executable, str(runner), str(args.engine.resolve()), str(args.archive.resolve()),
                       f"{args.model}{seed}.config", str(output.resolve())]
            subprocess.run(command, check=True)
            result = json.loads((output / "result.json").read_text())
            trajectory = output / "trajectory.json"
            raw = trajectory.read_bytes()
            assert hashlib.sha256(raw).hexdigest() == result["trajectory_sha256"]
            compressed = trajectory.with_suffix(".json.gz")
            with compressed.open("xb") as stream:
                stream.write(gzip.compress(raw, mtime=0))
            assert gzip.decompress(compressed.read_bytes()) == raw
            trajectory.unlink()  # This run's verified lossless gzip is its declared storage format.
            completed.write(json.dumps({"seed": seed, "command": command, "result": result,
                                        "compressed_sha256": hashlib.sha256(compressed.read_bytes()).hexdigest()}) + "\n")
            completed.flush()
            print(f"Archived {args.model} original seed {seed}", flush=True)

if __name__ == "__main__":
    main()
