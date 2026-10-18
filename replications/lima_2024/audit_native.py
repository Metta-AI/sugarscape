"""Reconcile completed native trajectories and every registered agent's location."""

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re

from audit_snapshot import Row

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("run", type=Path)
parser.add_argument("output", type=Path)
parser.add_argument("--jacamo-log", default="native.log")
args = parser.parse_args()
rows = [
    Row.model_validate_json(line)
    for line in (args.run / "snapshot-final.jsonl").read_bytes().splitlines()
]
initial = Counter(
    row.agent_id for row in rows if row.table != "router" and not row.path
)
assert initial and all(count == 1 for count in initial.values())
locations = Counter()
model_counts = {}
hashes = {}
for model in ("m1", "m2"):
    path = args.run / f"shared_volume/netlogo_output/{model}_output.txt"
    raw = path.read_bytes()
    hashes[str(path.relative_to(args.run))] = hashlib.sha256(raw).hexdigest()
    log = raw.decode()
    ticks = list(map(int, re.findall(r"NL: Tick number: \n(\d+)", log)))
    assert ticks == list(range(1000))
    assert log.count("NL: ---------- FIM DA SIMULACAO...") == 1
    assert log.count("NL: ---------- FIM!") == 1
    alive = args.run / f"shared_volume/netlogo_output/{model}_alive.txt"
    ids = list(map(int, alive.read_text().split()))
    assert len(ids) == len(set(ids))
    hashes[str(alive.relative_to(args.run))] = hashlib.sha256(
        alive.read_bytes()
    ).hexdigest()
    locations.update(ids)
    model_counts[model] = len(ids)
queued = Counter(row.agent_id for row in rows if not row.processed)
entered = Counter(row.agent_id for row in rows if row.table == "m3" and row.processed)
left = Counter(
    row.agent_id
    for row in rows
    if row.table == "router" and row.path.split("-")[-1] == "3"
)
assert not left - entered
active = entered - left
assert active.total() == 1
locations.update(queued)
locations.update(active)
assert locations == initial, {
    "missing": initial - locations,
    "extra": locations - initial,
}
native = (args.run / args.jacamo_log).read_text()
pattern = (
    r'Vai criar o agente com os beliefs: agent_id\((\d+)\),path\("([^"]*)"\), '
    r"sugar\((-?\d+)\), metabolism\((\d+)\), vision\((\d+)\)"
)
creations = Counter(
    (int(agent), path, f"[{sugar} {metabolism} {vision}]")
    for agent, path, sugar, metabolism, vision in re.findall(pattern, native)
)
expected = Counter(
    (row.agent_id, row.path, row.data)
    for row in rows
    if row.table == "m3" and row.processed
)
assert creations == expected
report = {
    "ticks_per_netlogo_model": 1000,
    "ordered_ticks_and_final_markers_verified": True,
    "netlogo_survivors": model_counts,
    "queued_agents": queued.total(),
    "active_jacamo_agents": dict(active),
    "registered_agents_accounted_for_once": initial.total(),
    "jacamo_native_attribute_reconstructions": creations.total(),
    "jacamo_returns": left.total(),
    "native_file_sha256": hashes,
    "scope": (
        "Complete native trajectories and identity conservation at "
        "shutdown; native JaCaMo creation attributes match consumed database records. "
        "This does not establish AgentSpeak reload or host-GUI scenario completion."
    ),
    "completed_study": False,
}
with args.output.open("x") as stream:
    stream.write(json.dumps(report, indent=2) + "\n")
print(json.dumps(report))
