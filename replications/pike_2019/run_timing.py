import argparse
import hashlib
import importlib
import json
import os
import platform
import random
import subprocess
import sys
import time
from pathlib import Path
import mesa
import numpy as np
import networkx

parser = argparse.ArgumentParser(
    description="Time 1000 native steps without the replication observer; retain native timing and raw outputs."
)
parser.add_argument("engine", type=Path)
parser.add_argument("library", type=Path)
directories = {
    "standard": "Initial/NetScape_Standard",
    "explicit": "Initial/NetScape_Brute",
    "network": "Initial/NetScape_Elegant",
    "groups-network": "Policy-Network",
    "policy-explicit": "Policy-Explicit",
    "common-one": "Common Resource- one level",
    "common-multi": "Common Resource- multi-level",
}
parser.add_argument("variant", choices=list(directories))
parser.add_argument("numpy_seed", type=int)
parser.add_argument("output", type=Path)
args = parser.parse_args()
for checkout, revision in [
    (args.engine, "585e53398f4f58e89ec184c83bb20819f0e4c96a"),
    (args.library, "99d2091721076df9fff32e8b49a0e33e98c34a6f"),
]:
    assert (
        subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=checkout, text=True
        ).strip()
        == revision
    )
    assert not subprocess.check_output(
        ["git", "status", "--porcelain", "--untracked-files=no"],
        cwd=checkout,
        text=True,
    ).strip()
assert mesa.__version__ == "0.8.5"
assert os.environ["PYTHONHASHSEED"] == "0"
sys.path.insert(0, str(args.library.resolve()))
root = args.engine.resolve() / directories[args.variant]
sys.path.insert(0, str(root))
NetScape = importlib.import_module("NetScape").NetScape
recorder = importlib.import_module("recorder")
N = importlib.import_module("NetAgent")

out = args.output.resolve()
out.mkdir(parents=True, exist_ok=False)
(out / "manifest.json").write_text(
    json.dumps(
        {
            "python": platform.python_version(),
            "mesa": mesa.__version__,
            "numpy": np.__version__,
            "networkx": networkx.__version__,
            "library_revision": "99d2091721076df9fff32e8b49a0e33e98c34a6f",
            "revision": "585e53398f4f58e89ec184c83bb20819f0e4c96a",
            "source_hashes": {
                p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                for p in root.glob("*.py")
            },
            "numpy_seed": args.numpy_seed,
            "policy_random_seed": args.numpy_seed,
            "pythonhashseed": os.environ["PYTHONHASHSEED"],
            "variant": args.variant,
            "runner_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "mesa_seed": 42,
            "steps": 1000,
        },
        indent=2,
    )
)
np.random.seed(args.numpy_seed)
random.seed(args.numpy_seed)
m = NetScape(seed=42)
registry = (
    m.schedule.agents_by_breed[N.NetAgent]
    if args.variant == "standard"
    else m.ml.agents_by_type[N.NetAgent]
)
assert len(registry) == 200
initial = [
    {
        "id": a.unique_id,
        "position": a.pos,
        "accumulations": a.accumulations,
        "metabolism": {k: int(v) for k, v in a.metabolism.items()},
    }
    for a in registry.values()
]
(out / "initial-agents.json").write_text(json.dumps(initial))
started_wall = time.perf_counter()
started_cpu = time.process_time()
for _ in range(1000):
    m.step()
cpu_seconds = time.process_time() - started_cpu
wall_seconds = time.perf_counter() - started_wall
native_times = m.datacollector.get_table_dataframe("Time")
assert len(native_times) == 1000
assert np.isfinite(native_times["Time Per Step"]).all()
assert (native_times["Time Per Step"] >= 0).all()
native_times.to_csv(out / "native-times.csv", index=False)
(out / "timing.json").write_text(
    json.dumps(
        {
            "steps": 1000,
            "full_step_wall_seconds": wall_seconds,
            "full_step_cpu_seconds": cpu_seconds,
            "native_timed_sections_seconds": float(native_times["Time Per Step"].sum()),
            "scope": "Native model timing excludes data collection and, in PhaseI groups, reassessment. Full loop timing includes every native step operation; initialization, exports and replication observers excluded.",
        },
        indent=2,
    )
    + "\n"
)
registry = (
    m.schedule.agents_by_breed[N.NetAgent]
    if args.variant == "standard"
    else m.ml.agents_by_type[N.NetAgent]
)
(out / "prices.json").write_text(json.dumps(m.price_record))
m.datacollector.get_model_vars_dataframe().to_csv(out / "population.csv", index=False)

m.datacollector.get_table_dataframe("Health").to_csv(out / "health.csv", index=False)

(out / "complete.json").write_text(
    json.dumps(
        {
            "steps": 1000,
            "native_reporter": recorder.survivors(m),
            "individual_agents": len(registry),
            "elapsed": wall_seconds,
        }
    )
)

(out / "exit.json").write_text(json.dumps({"exit_code": 0}))
