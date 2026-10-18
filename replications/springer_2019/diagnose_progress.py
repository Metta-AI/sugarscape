"""Observe native full-size progress without changing model rules or horizon."""

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("qualification", type=Path)
parser.add_argument("output", type=Path)
parser.add_argument("--architecture", choices=("61", "90"), required=True)
parser.add_argument("--control-mode", choices=("debug", "release"), required=True)
parser.add_argument(
    "--control-capacity", choices=("qualified", "native"), required=True
)
parser.add_argument("--control-only", action="store_true")
args = parser.parse_args()
root = args.output.resolve()
root.mkdir(parents=True, exist_ok=False)
hashes = json.loads((args.qualification / "effective-source-sha256.json").read_text())
for name, digest in hashes.items():
    assert (
        hashlib.sha256((args.qualification / "source" / name).read_bytes()).hexdigest()
        == digest
    )
shutil.copytree(args.qualification / "source", root / "source")
source = root / "source/dynasoar"
path = source / "example/sugarscape/dynasoar_no_cell/sugarscape.cu"
before = path.read_text()
observer = """
static int observed_iteration = -1;
static void progress(const char* phase) {
  if (observed_iteration < 2 || observed_iteration % 100 == 0) {
    auto now = std::chrono::steady_clock::now().time_since_epoch();
    auto micros = std::chrono::duration_cast<std::chrono::microseconds>(now).count();
    fprintf(stderr, "PROGRESS %d %lld %s\\n", observed_iteration, (long long)micros, phase);
    fflush(stderr);
  }
}
"""
after = before.replace("void step() {", observer + "\nvoid step() {")
assert before.count("void step() {") == 1
start = after.index("void step() {")
end = after.index("\n\n__global__ void create_cells()", start)
body = after[start:end]
lines = body.splitlines()
instrumented = []
for line in lines:
    if "<<<" in line or "allocator_handle->parallel_do<" in line:
        phase = line.strip().replace('"', "")
        instrumented.append(f'  progress("{phase}");')
    instrumented.append(line)
after = after[:start] + "\n".join(instrumented) + after[end:]
for statement in [
    "create_cells<<<128, 128>>>();",
    "create_agents<<<128, 128>>>();",
    "allocator_handle = new AllocatorHandle<AllocatorT>();",
    "initialize_simulation();",
]:
    assert after.count(statement) == 1
    after = after.replace(
        statement,
        f'progress("before {statement}");\n  '
        + statement
        + f'\n  progress("after {statement}");',
    )
old = """  for (int i = 0; i < kNumIterations; ++i) {
    step();
  }"""
assert after.count(old) == 1
after = after.replace(
    old,
    """  for (int i = 0; i < kNumIterations; ++i) {
    observed_iteration = i;
    progress("step-start");
    step();
    progress("step-complete");
  }""",
)
(root / "original-sugarscape.cu").write_text(before)
path.write_text(after)
(root / "observer-change.json").write_text(
    json.dumps(
        dict(
            original_sha256=hashlib.sha256(before.encode()).hexdigest(),
            observed_sha256=hashlib.sha256(after.encode()).hexdigest(),
            scope="Host stderr progress only; unchanged native rules, random calls, kernel launch order, synchronization calls and 10000-step horizon. Timings are diagnostic, not benchmark results.",
        ),
        indent=2,
    )
    + "\n"
)
records = []
probes = [(args.control_mode, 32, 60)]
if not args.control_only:
    probes += [("debug", 1700, 120), ("release", 1700, 120)]
for mode, size, limit in probes:
    label = f"{mode}-{size}"
    binary = root / label
    command = [
        "nvcc",
        "-O3",
        "-g" if mode == "debug" else "-DNDEBUG",
        "-std=c++11",
        "-lineinfo",
        "--expt-extended-lambda",
        "-gencode",
        f"arch=compute_{args.architecture},code=compute_{args.architecture}",
        "-maxrregcount=64",
        "-Iexample/configuration/dynasoar",
        "-I.",
        f"-DPARAM_SIZE={size}",
        "-Xcudafe",
        "--diag_suppress=1427",
        "example/sugarscape/dynasoar_no_cell/sugarscape.cu",
        "-o",
        str(binary),
    ]
    if size == 32 and args.control_capacity == "qualified":
        command.append("-DPARAM_MAX_OBJ=262144")
    with (root / f"{label}-build.log").open("x") as log:
        subprocess.run(
            command,
            cwd=source,
            stdout=log,
            stderr=subprocess.STDOUT,
            check=True,
            timeout=600,
        )
    with (root / f"{label}.stdout").open("x") as out, (root / f"{label}.stderr").open(
        "x"
    ) as err:
        result = subprocess.run(
            ["timeout", str(limit), str(binary)],
            cwd=source,
            stdout=out,
            stderr=err,
            timeout=limit + 10,
        )
    records.append(
        dict(
            mode=mode,
            grid_side=size,
            limit_seconds=limit,
            returncode=result.returncode,
            command=command,
            binary_sha256=hashlib.sha256(binary.read_bytes()).hexdigest(),
        )
    )
    (root / "records.json").write_text(json.dumps(records, indent=2) + "\n")
    if size == 32:
        assert result.returncode == 0
