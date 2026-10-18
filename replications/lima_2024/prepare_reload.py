"""Prepare the preregistered saved-agent control in a fresh container scenario."""

import argparse
import hashlib
import json
from pathlib import Path
import shutil

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("run", type=Path)
parser.add_argument("saved_agent", type=Path)
args = parser.parse_args()
assets = Path(__file__).parent
root = args.run.resolve()
assert not (root / "launch.json").exists()
assert not (root / "protocol.json").exists()
assert "jacamo" in json.loads((root / "compose.json").read_text())["services"]
protocol_path = assets / "reload-control-protocol.json"
protocol = json.loads(protocol_path.read_text())
assert (
    hashlib.sha256(args.saved_agent.read_bytes()).hexdigest()
    == protocol["saved_asl_sha256"]
)
source = root / "shared_volume/open_sugarscape_m1.nlogo"
before = source.read_bytes()
pins = json.loads((assets / "source-pins.json").read_text())
assert (
    hashlib.sha256(before).hexdigest()
    == pins["files"]["shared_volume/open_sugarscape_m1.nlogo"]
)
change = json.loads(
    (assets / "results/reload-first-event-2026-10-18/source-change.json").read_text()
)
old, new = change["old"], change["new"]
assert before.decode().count(old) == 1
source.write_text(before.decode().replace(old, new))
assert hashlib.sha256(source.read_bytes()).hexdigest() == change["after_sha256"]
shutil.copyfile(args.saved_agent, root / "agent-399-input.asl")
shutil.copyfile(protocol_path, root / "protocol.json")
(root / "source-change.json").write_text(
    json.dumps(
        {
            "file": "shared_volume/open_sugarscape_m1.nlogo",
            "old": old,
            "new": new,
            "before_sha256": hashlib.sha256(before).hexdigest(),
            "after_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        },
        indent=2,
    )
    + "\n"
)
(root / "initial-checkpoints.json").write_text(
    json.dumps(
        [
            {
                "table": "m3",
                "id": 1,
                "agent_id": 399,
                "data": "[0 3 6]",
                "path": "1-3",
                "asl_file_path": "",
            }
        ],
        indent=2,
    )
    + "\n"
)
