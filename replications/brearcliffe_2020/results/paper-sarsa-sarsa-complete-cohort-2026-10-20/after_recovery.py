"""Audit the disjoint final cohort from sealed original and recovery evidence."""
from pathlib import Path
import csv
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tarfile
import time

root = Path(__file__).resolve().parent
evidence = root.parent
repo = evidence.parent / 'sugarscape-brearcliffe/replications/brearcliffe_2020'
collector = evidence / 'storage-handoff-20261017-001/brearcliffe-paper-recovery-restored-001'
status_path = collector / 'batch-results.tar.gz.status.json'
plan = json.loads((root / 'plan.json').read_bytes())
for name, digest in plan['source_sha256'].items():
    assert hashlib.sha256(Path(name).read_bytes()).hexdigest() == digest
assert not (root / 'recovery.tar.gz').exists()
deadline = time.monotonic() + 10800
while not status_path.exists() or json.loads(status_path.read_bytes())['status'] != 'complete':
    assert time.monotonic() < deadline
    observed = subprocess.run(['ps', '-p', str(plan['collector_pid']), '-o', 'stat='], capture_output=True, text=True, timeout=10)
    assert observed.returncode == 0 and not observed.stdout.strip().startswith('Z'), 'Collector ended before sealed export'
    time.sleep(30)
receipt = json.loads((collector / 'batch-results.tar.gz.intent.json').read_bytes())['receipt']
assert receipt['bytes'] <= 134217728
assert shutil.disk_usage(root).free > 2 * 1024**3
key = 'relh-sugarscape-evidence-20261017/brearcliffe-paper-recovery-restored-001/batch-results.tar.gz'
with (root / 'download.json').open('x') as log:
    subprocess.run(['autor', 'storage', 'cp', key, str(root / 'recovery.tar.gz'), '--json'], stdout=log, check=True, timeout=600)
archive = root / 'recovery.tar.gz'
assert archive.stat().st_size == receipt['bytes']
assert hashlib.sha256(archive.read_bytes()).hexdigest() == receipt['sha256']
extracted = root / 'recovery'
extracted.mkdir()
with tarfile.open(archive) as bundle:
    members = bundle.getmembers()
    assert len({m.name for m in members}) == len(members)
    assert all(m.isfile() or m.isdir() for m in members)
    assert all(not Path(m.name).is_absolute() and '..' not in Path(m.name).parts for m in members)
    bundle.extractall(extracted, filter='data')
terminal = json.loads((extracted / 'batch/terminal.json').read_bytes())
assert terminal['exit_code'] == 0 and terminal['successful_inputs'] == terminal['attempted_inputs'] == 44
assert terminal['unstarted_inputs'] == 0
assert json.loads((extracted / 'wrapper-terminal.json').read_bytes())['batch_exit_code'] == 0
assignment = evidence / 'brearcliffe-paper-recovery-001/remaining.csv'
assert (extracted / 'remaining.csv').read_bytes() == assignment.read_bytes()
with assignment.open() as stream:
    assigned = {row['run_id'] for row in csv.DictReader(stream)}
attempts = [json.loads(line) for line in (extracted / 'batch/attempts.jsonl').read_text().splitlines()]
assert len(attempts) == 44 and {r['run_id'] for r in attempts} == assigned
assert all(r['exit_code'] == 0 for r in attempts)
original = evidence / 'brearcliffe-paper-terminal-reconciliation-001'
prior = json.loads((original / 'union-audit/audit.json').read_bytes())
old_final = [r for r in prior['completed'] if r['run_id'].startswith('paper-table-pair-15-repeat-')]
assert len(old_final) == 6 and not assigned.intersection(r['run_id'] for r in prior['completed'])
runs = [Path(r['directory']) for r in old_final] + sorted((extracted / 'batch/runs').iterdir())
assert len(runs) == 50 and {p.name for p in runs} == {f'paper-table-pair-15-repeat-{i:02d}' for i in range(50)}
for row in old_final:
    assert hashlib.sha256((Path(row['directory']) / 'trajectory.csv').read_bytes()).hexdigest() == row['trajectory_sha256']
pins = {}
sealed = root / 'paper-pair15-50.tar.gz'
with tarfile.open(sealed, 'x:gz') as bundle:
    for run in sorted(runs):
        for path in sorted(run.rglob('*')):
            assert not path.is_symlink()
            if path.is_file():
                name = 'runs/' + run.name + '/' + str(path.relative_to(run))
                data = path.read_bytes()
                pins[name] = {'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}
                bundle.add(path, arcname=name, recursive=False)
snapshot = {'inputs': 50, 'original_inputs': 6, 'recovery_inputs': 44, 'archive_bytes': sealed.stat().st_size, 'archive_sha256': hashlib.sha256(sealed.read_bytes()).hexdigest(), 'files': pins, 'recovery_storage_key': key, 'recovery_archive_sha256': receipt['sha256'], 'scope': 'Disjoint final cohort assembled locally from independently archived original and recovery runs. No new simulations.'}
(root / 'snapshot.json').write_text(json.dumps(snapshot, indent=2) + '\n')
env = {**os.environ, 'R_LIBS_USER': str(evidence.parent / 'sugarscape-replication-tools/R-library')}
commands = [
    [sys.executable, str(root / 'readback.py')],
    ['/opt/homebrew/bin/Rscript', '--vanilla', str(repo / 'verify_cohort.R'), str(evidence / 'brearcliffe-ensemble-preparation-001'), str(root / 'union-audit/audit.json'), str(root / 'cohort'), str(root / 'r-validation.json')],
    [sys.executable, str(repo / 'compare_curves.py'), str(root / 'cohort'), str(repo / 'results/horizontal-calibration-correction-2026-10-19/metric-curves.json.gz'), str(root / 'comparison')],
]
for index, command in enumerate(commands):
    with (root / f'analysis-{index}.log').open('x') as log:
        subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, check=True, timeout=900, env=env)
(root / 'analysis-terminal.json').write_text(json.dumps({'exit_code': 0, 'cohort_inputs': 50, 'union_inputs': 1600, 'scope': 'Native trajectories, cohort arithmetic, independent R checks and descriptive curve comparison complete. Final cohort remote archive, publication, whole-study claims and verdict remain pending.'}, indent=2) + '\n')
