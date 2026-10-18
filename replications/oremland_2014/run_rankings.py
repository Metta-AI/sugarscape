"""Run the declared ranking jobs with a qualified compressed-input pipeline."""

import argparse
from concurrent.futures import ThreadPoolExecutor
import gzip
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("java_home", type=Path)
parser.add_argument("netlogo_app", type=Path)
parser.add_argument("experiment", type=Path)
parser.add_argument("--timeout", type=Path, required=True)
parser.add_argument("--gzip", type=Path, required=True)
args = parser.parse_args()
root = args.experiment.resolve()
protocol = json.loads((root / "protocol.json").read_text())
assert (
    protocol["workers"] == 4
    and protocol["global_execution_limit_seconds"] == 3600
    and protocol["per_job_limit_seconds"] == 1800
)
assert (
    hashlib.sha256((root / "policies.json").read_bytes()).hexdigest()
    == protocol["policies_sha256"]
)
assert (
    hashlib.sha256((root / "reduction-protocol.json").read_bytes()).hexdigest()
    == protocol["reduction_protocol_sha256"]
)
run = root / "execution"
run.mkdir(exist_ok=False)
source = Path(__file__).with_name("RunPolicyBatch.java")
(run / source.name).write_bytes(source.read_bytes())
(run / Path(__file__).name).write_bytes(Path(__file__).read_bytes())
config = (args.netlogo_app / "NetLogo.cfg").read_text().splitlines()
assert "app.version=5.3.1" in config
names = next(
    line.split("=", 1)[1] for line in config if line.startswith("app.classpath=")
).split(":")
jars = [args.netlogo_app / name for name in ["NetLogo.jar", *names]]
classpath = ":".join(str(path.resolve()) for path in jars) + ":" + str(run)
compile_command = [
    str(args.java_home / "bin/javac"),
    "-cp",
    classpath,
    "-d",
    str(run),
    str(run / source.name),
]
subprocess.run(compile_command, check=True)
java_prefix = [
    str(args.java_home / "bin/java"),
    "-Xmx512m",
    "-XX:ActiveProcessorCount=1",
    "-Djava.awt.headless=true",
    "-Dfile.encoding=UTF-8",
    "-cp",
    classpath,
    "RunPolicyBatch",
]
reference = Path(__file__).parent / "results/headless-batch-evaluator-2026-10-18"
reference_manifest = json.loads((reference / "manifest.json").read_text())
jar_hashes = {
    path.name: hashlib.sha256(path.read_bytes()).hexdigest()
    for path in jars
    if path.is_file()
}
assert jar_hashes == reference_manifest["jars"]
assert (
    hashlib.sha256(source.read_bytes()).hexdigest()
    == reference_manifest["source_sha256"]
)
manifest = {
    "compile_command": compile_command,
    "java_prefix": java_prefix,
    "launcher_pid": os.getpid(),
    "started_unix": time.time(),
    "sha256": {
        path.name: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in [
            root / "protocol.json",
            run / source.name,
            run / "RunPolicyBatch.class",
            Path(__file__),
        ]
    },
    "jars": jar_hashes,
    "missing_declared_jars": [path.name for path in jars if not path.is_file()],
}
(run / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")


def execute_pipeline(requests, model, output, seconds, prefix):
    """Stream retained gzip inputs through the qualified native evaluator."""
    command = [
        str(args.timeout),
        "--signal=TERM",
        "--kill-after=30",
        str(seconds),
        *java_prefix,
        str(model),
        "/dev/stdin",
        str(output),
    ]
    decompress_command = [str(args.gzip), "-dc", str(requests)]
    started = time.time()
    with prefix.with_suffix(".log").open("x") as stream:
        producer = subprocess.Popen(
            decompress_command, stdout=subprocess.PIPE, stderr=stream
        )
        try:
            consumer = subprocess.Popen(
                command, stdin=producer.stdout, stdout=stream, stderr=subprocess.STDOUT
            )
            producer.stdout.close()
            prefix.with_suffix(".json").write_text(
                json.dumps(
                    {
                        "producer_pid": producer.pid,
                        "consumer_pid": consumer.pid,
                        "started_unix": started,
                        "command": command,
                        "decompress_command": decompress_command,
                    },
                    indent=2,
                )
                + "\n"
            )
            code = consumer.wait()
            producer_code = producer.wait()
        finally:
            if producer.poll() is None:
                producer.terminate()
                producer.wait()
    result = {
        "exit_code": code,
        "decompress_exit_code": producer_code,
        "elapsed_seconds": time.time() - started,
    }
    prefix.with_suffix(".exit.json").write_text(json.dumps(result, indent=2) + "\n")
    return result


# Qualify this actual stdin/decompression path before starting any new scientific job.
full_model = Path(protocol["full_size_reference"]) / "execution/oremland.nlogo"
assert (
    hashlib.sha256(full_model.read_bytes()).hexdigest()
    == reference_manifest["model_sha256"]
)
preflight = execute_pipeline(
    reference / "requests.jsonl.gz",
    full_model,
    run / "pipeline-reference.jsonl",
    120,
    run / "pipeline-reference",
)
assert preflight["exit_code"] == preflight["decompress_exit_code"] == 0
with gzip.open(reference / "results.jsonl.gz", "rt") as stream:
    expected = [json.loads(line) for line in stream]
actual = [
    json.loads(line)
    for line in (run / "pipeline-reference.jsonl").read_text().splitlines()
]
assert len(actual) == len(expected) == 400
for before, after in zip(expected, actual, strict=True):
    del before["elapsed_seconds"]
    del after["elapsed_seconds"]
    assert before == after
(run / "pipeline-audit.json").write_text(
    json.dumps(
        {
            "exact_complete_native_reference_matches": 400,
            "reference_manifest_sha256": hashlib.sha256(
                (reference / "manifest.json").read_bytes()
            ).hexdigest(),
        },
        indent=2,
    )
    + "\n"
)
started = time.monotonic()


def execute(job):
    """Validate and execute one disjoint retained request shard within the budget."""
    requests = root / job["requests"]
    model = requests.parent / "oremland.nlogo"
    assert (
        hashlib.sha256(requests.read_bytes()).hexdigest() == job["requests_gz_sha256"]
    )
    assert hashlib.sha256(model.read_bytes()).hexdigest() == job["model_sha256"]
    assert (
        hashlib.sha256(model.with_name("sugar-map.txt").read_bytes()).hexdigest()
        == job["landscape_sha256"]
    )
    seconds = min(1800, int(3600 - (time.monotonic() - started)))
    name = job["model"] + "-shard-" + str(job["shard"])
    if seconds <= 0:
        result = {
            "exit_code": 125,
            "reason": "Global execution budget exhausted before job start",
        }
        (run / (name + ".exit.json")).write_text(json.dumps(result, indent=2) + "\n")
        return result
    return execute_pipeline(
        requests, model, run / (name + ".results.jsonl"), seconds, run / name
    )


with ThreadPoolExecutor(max_workers=4) as executor:
    results = list(executor.map(execute, protocol["jobs"]))
(run / "exit.json").write_text(
    json.dumps(
        {"jobs": results, "elapsed_seconds": time.monotonic() - started}, indent=2
    )
    + "\n"
)
assert all(
    result["exit_code"] == 0 and result["decompress_exit_code"] == 0
    for result in results
)
