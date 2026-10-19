set -eu
cd /root/sugarscape/blueprints-bentham-disk-recovery-001
mv source-sha256.json failed-payload-manifest.json
mv qualification qualification-failed-manifest
cp /root/correct-source-sha256.json source-sha256.json
venv/bin/python qualify.py
set +e
venv/bin/python run_selected.py engine blueprints-homogeneous.zip plan.json runs
rc=$?
set -e
printf '%s\n' "$rc" > exit-code.txt
venv/bin/python -c 'import json; from pathlib import Path; assert not json.loads(Path("runs/termination.json").read_text())["remaining_live_groups"]'
tar -czf terminal-evidence.partial.tar.gz runs qualification qualification-failed-manifest failed-payload-manifest.json plan.json source-sha256.json run_selected.py run_batch.py run.py audit_batch.py bootstrap.log recovery.log exit-code.txt
mv terminal-evidence.partial.tar.gz terminal-evidence.tar.gz
exit "$rc"
