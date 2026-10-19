from pathlib import Path
import json
import subprocess

base = Path(__file__).resolve().parent
out = base / 'blueprints-source-checkpoint-002'
out.mkdir()
repo = base.parent / 'sugarscape-blueprints'
python = str(base.parent / 'sugarscape-replications/.venv/bin/python')
archive = str(base / 'papers/blueprints-homogeneous.zip')
previous = base / 'blueprints-source-reaudit-001'
reports = []
active = {f'blueprints-2024-resumed-{model}-{suffix}' for model, suffix in [
    ('rawSugarscape', '006'), ('altruisticHalfLookaheadBinary', '005'),
    ('egoisticHalfLookaheadBinary', '005'), ('benthamHalfLookaheadBinary', '005')]}
for report in sorted(previous.glob('*/audit.json')):
    name = report.parent.name
    if name in active:
        command = [python, str(repo / 'replications/blueprints_2024/audit_batch.py'), archive,
                   str(base / name), str(out / name), '--allow-prefix']
        with (out / (name + '.log')).open('w') as log:
            subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, check=True)
        report = out / name / 'audit.json'
        print(name, json.loads(report.read_text())['runs'], flush=True)
    reports.append(str(report))
assert len(reports) == 24
command = [python, str(repo / 'replications/blueprints_2024/reconcile_coverage.py'), archive,
           str(out / 'coverage'), *reports]
(out / 'command.json').write_text(json.dumps(command, indent=2) + '\n')
with (out / 'coverage.log').open('w') as log:
    subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, check=True)
print((out / 'coverage.log').read_text())
