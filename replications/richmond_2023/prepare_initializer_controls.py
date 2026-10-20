"""Prepare all eight initializer interpretations on the qualified four-rule control."""

import argparse
import difflib
import hashlib
import itertools
import json
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("qualified_variants", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
pins = {
    "released": "307bb4829ffef97b9eb004bdc59b58282aebd937c0bd4138581753bef711fba4",
    "combined_with_counter_reset": "5b708cbc7da876a7dd7a4a9692c09be06f28479ea27b15e974464f5048e6d0f5",
}
sources = {}
for name, digest in pins.items():
    raw = (args.qualified_variants / name / "src/main.cu").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == digest
    sources[name] = raw.decode()

# Capture all cells at initialization without changing the active-state trajectory.
anchor = "                                if (status != AGENT_STATUS_UNOCCUPIED) {"
initial_observer = '                                if (step == -1) {\n                                    initial_csv << step << "," << instance.getVariable<int>("agent_id") << ","\n                                        << instance.getVariable<unsigned int, 2>("pos", 0) << ","\n                                        << instance.getVariable<unsigned int, 2>("pos", 1) << ","\n                                        << status << "," << instance.getVariable<int>("sugar_level") << ","\n                                        << instance.getVariable<int>("metabolism") << ","\n                                        << instance.getVariable<int>("env_sugar_level") << ","\n                                        << instance.getVariable<int>("env_max_sugar_level") << "\\n";\n                                }\n'
records = []
args.output.mkdir(parents=True, exist_ok=False)
conditions = [("released", "released", 4, 4, False)]
for metabolism, capacity, wrapped in itertools.product([4, 5], [4, 7], [False, True]):
    name = f"combined_m{metabolism}_c{capacity}_{'wrapped' if wrapped else 'direct'}"
    conditions.append(
        (name, "combined_with_counter_reset", metabolism, capacity, wrapped)
    )
for name, parent, metabolism, capacity, wrapped in conditions:
    original = sources[parent]
    text = original
    edits = [
        ("#define MAX_INIT_METABOLISM 4", f"#define MAX_INIT_METABOLISM {metabolism}"),
        (
            "#define ENV_SUGAR_MAX_CAPACITY 4",
            f"#define ENV_SUGAR_MAX_CAPACITY {capacity}",
        ),
    ]
    if wrapped:
        old = "float hs_dist = static_cast<float>(sqrt(pow(hs_x - static_cast<int>(x), 2.0f) + pow(hs_y - static_cast<int>(y), 2.0f)));"
        new = "int dx = std::abs(hs_x - static_cast<int>(x));\n                                    int dy = std::abs(hs_y - static_cast<int>(y));\n                                    dx = std::min(dx, static_cast<int>(gridWidth) - dx);\n                                    dy = std::min(dy, static_cast<int>(gridWidth) - dy);\n                                    float hs_dist = static_cast<float>(sqrt(pow(dx, 2.0f) + pow(dy, 2.0f)));"
        edits.append((old, new))
    declaration = '                        std::ofstream state_csv("state.csv");'
    edits.extend(
        [
            (
                declaration,
                declaration
                + "\n"
                + '                        std::ofstream initial_csv("initial-cells.csv");\n                        initial_csv << "step,id,x,y,status,sugar,metabolism,cell_sugar,cell_capacity\\n";',
            ),
            (anchor, initial_observer + anchor),
            (
                "                        record_state(-1);",
                "                        record_state(-1);\n                        initial_csv.flush();\n                        if (!initial_csv) std::abort();",
            ),
        ]
    )
    for old, new in edits:
        assert text.count(old) == 1
        text = text.replace(old, new)
    restored = text
    for old, new in reversed(edits):
        assert restored.count(new) == 1
        restored = restored.replace(new, old)
    assert restored == original
    directory = args.output / name
    directory.mkdir()
    (directory / "main.cu").write_text(text)
    patch = "".join(
        difflib.unified_diff(
            original.splitlines(keepends=True),
            text.splitlines(keepends=True),
            fromfile="a/src/main.cu",
            tofile="b/src/main.cu",
        )
    )
    (directory / "changes.patch").write_text(patch)
    records.append(
        {
            "variant": name,
            "parent": parent,
            "metabolism_maximum": metabolism,
            "capacity_maximum": capacity,
            "wrapped_cell_distances": wrapped,
            "source_sha256": hashlib.sha256(text.encode()).hexdigest(),
            "patch_sha256": hashlib.sha256(patch.encode()).hexdigest(),
            "reverse_exact": True,
        }
    )
report = {
    "parent_sha256": pins,
    "variants": records,
    "scope": "Preparation only. Released replay plus complete 2x2x2 initializer factorial on the qualified transfer/cardinal/nonpositive-death/counter-reset control. Parent scheduling, peak generation, seed and nine-round cap unchanged. No native execution or fully specified paper implementation claimed.",
}
(args.output / "manifest.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report))
