"""Extract pinned host initialization, replacing engine storage writes with CSV output."""

import argparse
import hashlib
import json
from pathlib import Path
import re

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("source", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
raw = args.source.read_bytes()
assert (
    hashlib.sha256(raw).hexdigest()
    == "b2daf9e6ee2b3faf4a13e30ba19f4293e1f922a993d30cb5e72fb1d4c2b8f56d"
)
source = raw.decode()
constants = re.findall(
    r"^#define (?:AGENT_STATUS_\w+|ENV_SUGAR_MAX_CAPACITY|MIN_HOTSPOT_DISTANCE|MIN_INIT_AGENT_SUAGR_WEALTH|MAX_INIT_AGENT_SUAGR_WEALTH|MIN_INIT_METABOLISM|MAX_INIT_METABOLISM) .+$",
    source,
    re.M,
)
distance = source[
    source.index("bool hotspot_distance_check(") : source.index(
        "typedef struct Experiment"
    )
]
assert distance.rstrip().endswith("}")
first = source.index(
    "std::mt19937_64 rng(cudaSimulation.getSimulationConfig().random_seed);"
)
last = source.index("#ifdef VISUALISATION", first)
body = source[first:last]
replacements = {
    "cudaSimulation.getSimulationConfig().random_seed": "seed",
    'flamegpu::AgentVector init_pop(model.Agent("agent"), CELL_COUNT);': "",
    "const unsigned int CELL_COUNT = gridWidth * gridWidth;": "",
    "unsigned int i = 0;": "",
    "flamegpu::AgentVector::Agent instance = init_pop[i++];": "int id = -1, status = 0, sugar = 0, metabolism = 0, cell_sugar = 0, cell_capacity = 0;",
    'instance.setVariable<unsigned int, 2>("pos", { x, y });': "",
    'std::cout << "Warning:': 'std::cerr << "Warning:',
}
for old, new in replacements.items():
    assert body.count(old) == 1, old
    body = body.replace(old, new)
variables = {
    "agent_id": "id",
    "status": "status",
    "sugar_level": "sugar",
    "metabolism": "metabolism",
    "env_sugar_level": "cell_sugar",
    "env_max_sugar_level": "cell_capacity",
}
for variable, local in variables.items():
    body, count = re.subn(
        r'instance\.setVariable<int>\("' + variable + r'", ([^;]+)\);',
        local + r" = \1;",
        body,
    )
    assert count == (1 if variable.startswith("env_") else 2), variable
marker = "// Currently population has not been init, so generate an agent population on the fly"
assert body.count(marker) == 1
body = body.replace(
    marker,
    'for (const auto& hotspot : sugar_hotspots) { std::cerr << "HOTSPOT," << hotspot[0] << "," << hotspot[1] << "\\n"; }\n'
    + marker,
)
assert "instance." not in body and "flamegpu::" not in body
prefix = "\n".join(
    [
        "#include <algorithm>",
        "#include <array>",
        "#include <cmath>",
        "#include <iostream>",
        "#include <random>",
        "#include <vector>",
        *constants,
    ]
)
main = """
int main() {
    const unsigned int gridWidth = 256;
    const unsigned long long seed = 0;
    const float pOccupation = 0.17f;
    std::cout << "step,id,x,y,status,sugar,metabolism,cell_sugar,cell_capacity\\n";
"""
end = """
    std::cout << -1 << ',' << id << ',' << x << ',' << y << ',' << status << ',' << sugar << ',' << metabolism << ',' << cell_sugar << ',' << cell_capacity << '\\n';
    }
    }
}
"""
args.output.mkdir(exist_ok=False)
cpp = prefix + "\n" + distance + main + body + end
(args.output / "initial.cpp").write_text(cpp)
report = {
    "source_sha256": hashlib.sha256(raw).hexdigest(),
    "extracted_cpp_sha256": hashlib.sha256(cpp.encode()).hexdigest(),
    "condition": {"seed": 0, "width": 256, "occupation": 0.17},
    "extraction": "Retain original distance function, constants, hotspot generation, agent random draws, loop order and landscape arithmetic. Replace engine storage assignments with local integers and CSV writes; route original warning and hotspot coordinates to stderr. No engine simulation steps.",
    "native_parity": "Unverified until comparison against pending native initial-state capture. Compiler/library distribution differences remain possible.",
}
(args.output / "extraction.json").write_text(json.dumps(report, indent=2) + "\n")
