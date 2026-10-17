set -eu
/root/sugarscape/blueprints-runtime-recovery-001/source/venv/bin/python -c 'import hashlib,json,shutil
from pathlib import Path
pins={'"'"'/root/sugarscape/blueprints-runtime-recovery-001/runs/run_recovery.py'"'"': '"'"'db26af7b7d3b910aa1537f7f4d5b2d51655862b6103e98a796acd6774e9b2e4b'"'"', '"'"'/root/sugarscape/blueprints-runtime-recovery-001/runs/terminal.json'"'"': '"'"'cb5aae11ebeeb25b7d0d800e737d8ff82a07b03f3659b4cf0e2d77180213714d'"'"', '"'"'/root/sugarscape/blueprints-runtime-recovery-001/runs/rawSugarscape-50000/completed.jsonl'"'"': '"'"'428f329848687ec8dba5fad633001925adb4a76e043dbd146272a682d76988d4'"'"', '"'"'/root/sugarscape/blueprints-runtime-recovery-001/runs/altruisticHalfLookaheadBinary-5000/completed.jsonl'"'"': '"'"'d5ced9a2c669f87a75b6e22a97e8a79e3cbc4a41dd68625d9be9505bff7f36f3'"'"'}
for path,digest in pins.items():assert hashlib.sha256(Path(path).read_bytes()).hexdigest()==digest,path
assert shutil.disk_usage('"'"'/root'"'"').free >= 8*1024**3
root=Path('"'"'/root/sugarscape/blueprints-runtime-recovery-002'"'"');root.mkdir(exist_ok=False)
(root/'"'"'plan.json'"'"').write_text('"'"'{"groups": [{"model": "rawSugarscape", "steps": 50000, "start": 27, "stop": 100}, {"model": "altruisticHalfLookaheadBinary", "steps": 50000, "start": 0, "stop": 100}], "seconds_per_group": 21600, "checkpoint_seconds": 1800}'"'"'+'"'"'\n'"'"')
'
exec timeout 23400 /root/sugarscape/blueprints-runtime-recovery-001/source/venv/bin/python /root/sugarscape/blueprints-runtime-recovery-001/runs/run_recovery.py /root/sugarscape/blueprints-runtime-recovery-001/source /root/sugarscape/blueprints-runtime-recovery-002/plan.json /root/sugarscape/blueprints-runtime-recovery-002/runs
