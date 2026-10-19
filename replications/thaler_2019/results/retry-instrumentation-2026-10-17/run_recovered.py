"""Run complete original instrumented simulations and retain cumulative counters."""

import hashlib
import json
import shutil
import subprocess
import time
from pathlib import Path

root = Path(__file__).resolve().parent
protocol = json.loads((root / "protocol.json").read_text())
for name, digest in json.loads((root / "auxiliary-source-sha256.json").read_text()).items():
    assert hashlib.sha256((root / name).read_bytes()).hexdigest() == digest
started = time.monotonic()
for variant in ["tvar", "tarray"]:
    project = root / variant
    assert shutil.disk_usage(root).free >= 4 * 1024**3
    for name, digest in protocol["source_sha256"].items():
        prefix = f"criterion/sugarscape-{variant}/"
        if name.startswith(prefix):
            relative = Path(name).relative_to(prefix)
            expected = protocol["changes"][variant]["instrumented_sha256"] if str(relative) == "src/Main.hs" else digest
            assert hashlib.sha256((project / relative).read_bytes()).hexdigest() == expected
    output = root / "recovered-runs" / variant
    output.mkdir(parents=True, exist_ok=False)
    with (output / "build.log").open("wb") as log:
        subprocess.run(
            ["stack", "build", "--jobs", "1"],
            cwd=project,
            stdout=log,
            stderr=subprocess.STDOUT,
            check=True,
            timeout=max(1, 1800 - (time.monotonic() - started)),
        )
    compiler = subprocess.check_output(
        ["stack", "exec", "--", "ghc", "--numeric-version"], cwd=project, text=True
    ).strip()
    assert compiler == "8.4.3"
    install = subprocess.check_output(["stack", "path", "--local-install-root"], cwd=project, text=True).strip()
    binary = Path(install) / "bin" / f"sugarscape-{variant}"
    command = [
        str(binary),
        "--iters",
        "2",
        "--match",
        "prefix",
        f"sugarscape-{variant}-normal:1/500",
        "+RTS",
        "-N1",
        "-RTS",
    ]
    manifest = {
        "command": command,
        "compiler": compiler,
        "binary_sha256": hashlib.sha256(binary.read_bytes()).hexdigest(),
    }
    (output / "command.json").write_text(json.dumps(manifest, indent=2) + "\n")
    before = time.monotonic()
    with (output / "stdout.log").open("wb") as stdout, (output / "stderr.log").open("wb") as stderr:
        result = subprocess.run(
            command,
            cwd=project,
            stdout=stdout,
            stderr=stderr,
            timeout=min(600, max(1, 1800 - (time.monotonic() - started))),
        )
    (output / "exit.json").write_text(
        json.dumps({"exit_code": result.returncode, "elapsed_seconds": time.monotonic() - before}) + "\n"
    )
    result.check_returncode()
    print(json.dumps({"variant": variant, "exit_code": result.returncode}), flush=True)
(root / "complete.json").write_text(json.dumps({"completed_processes": 2}) + "\n")
