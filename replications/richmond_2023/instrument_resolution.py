"""Add passive host-counter logging and stop after the first full condition."""

import argparse
import difflib
import hashlib
import json
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("source", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
original = args.source.read_bytes()
assert (
    hashlib.sha256(original).hexdigest()
    == "b2daf9e6ee2b3faf4a13e30ba19f4293e1f922a993d30cb5e72fb1d4c2b8f56d"
)
text = original.decode()
needle = "                            cudaSimulation.step();"
assert text.count(needle) == 2
replacement = """                            const unsigned int counter_before = exit_condition_iterations;
                            cudaSimulation.step();
                            std::cerr << "RESOLUTION_TRACE," << experiment.title << "," << repetition << "," << gridWidth << "," << i << "," << counter_before << "," << exit_condition_iterations << std::endl;"""
text = text.replace(needle, replacement)
needle = '                        csv << repetition << "," << gridWidth << "," << popSize << "," << pOccupation << "," << averageStepTime << "," << averagePopCount << std::endl;'
assert text.count(needle) == 1
text = text.replace(
    needle,
    needle
    + "\n                        return 0;  // Diagnostic ends after the first complete 100-step condition.",
)
args.output.mkdir(parents=True, exist_ok=False)
(args.output / "main.cu").write_text(text)
(args.output / "observer.patch").write_text(
    "".join(
        difflib.unified_diff(
            original.decode().splitlines(True),
            text.splitlines(True),
            fromfile="original/src/main.cu",
            tofile="observer/src/main.cu",
        )
    )
)
(args.output / "protocol.json").write_text(
    json.dumps(
        {
            "original_sha256": hashlib.sha256(original).hexdigest(),
            "observer_sha256": hashlib.sha256(text.encode()).hexdigest(),
            "condition": {"seed": 0, "width": 256, "occupation": 0.17, "steps": 100},
            "measurement": "Global resolution counter immediately before and after each native step",
            "expected_parity": "All100 population observations must equal the unmodified qualification prefix before interpretation",
            "timing_scope": "Instrumented execution excluded from performance comparison",
            "model_changes": [],
            "execution_scope_change": "Return after first complete condition; no full-ensemble credit",
        },
        indent=2,
    )
    + "\n"
)
