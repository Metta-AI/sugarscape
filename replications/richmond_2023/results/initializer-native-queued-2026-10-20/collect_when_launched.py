from pathlib import Path
import json
import subprocess
import sys
import time
root = Path(__file__).resolve().parent
clock = json.loads((root/"startup-clock.json").read_text())
while not (root/"launch.json").exists():
    if (root/"startup-bound-stop.json").exists():
        raise SystemExit("Startup bound reached; no producer to collect")
    assert time.time() < clock["started_unix"] + 1080
    time.sleep(10)
receipt = json.loads((root/"launch.json").read_text())
assert receipt["exit_code"] == 0
command = json.loads(receipt["stdout"])["command_id"]
args = [sys.executable,str(root/"collect_storage_bounded.py"),"relh-sugarscape-richmond-h100-20261017-v1",command,"richmond-initializer-native-controls-terminal-001","--seconds","4560","--max-bytes",str(256*1024**2),"--terminal-file","/root/sugarscape/richmond-initializer-native-controls-001/native-evidence.tar.gz"]
(root/"collector-command.json").write_text(json.dumps(args,indent=2)+"\n")
subprocess.run(args,check=True)
