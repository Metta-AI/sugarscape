"""Preserve the final cohort and compute full declared comparisons; no verdict."""
from pathlib import Path
import hashlib
import json
import os
import subprocess
import sys
import tarfile
import time

root = Path(__file__).resolve().parent
evidence = root.parent
repo = evidence.parent / 'sugarscape-brearcliffe/replications/brearcliffe_2020'
plan = json.loads((root / 'synthesis-plan.json').read_bytes())
for name, digest in plan['source_sha256'].items():
    assert hashlib.sha256(Path(name).read_bytes()).hexdigest() == digest
preflight = json.loads((root / 'storage-preflight.json').read_bytes())
assert preflight['objects'] == [] and not preflight['truncated']
deadline = time.monotonic() + 14400
while not (root / 'analysis-terminal.json').exists():
    assert time.monotonic() < deadline
    state = subprocess.run(['ps', '-p', '65164', '-o', 'stat='], capture_output=True, text=True, timeout=10)
    assert state.returncode == 0 and not state.stdout.strip().startswith('Z'), 'Cohort watcher ended before audited completion'
    time.sleep(30)
assert json.loads((root / 'analysis-terminal.json').read_bytes())['exit_code'] == 0
for name, digest in plan['source_sha256'].items():
    assert hashlib.sha256(Path(name).read_bytes()).hexdigest() == digest
assert subprocess.check_output(['git', '-C', str(repo), 'rev-parse', 'HEAD'], text=True).strip() == plan['repository_head']
snapshot = json.loads((root / 'snapshot.json').read_bytes())
archive = root / 'paper-pair15-50.tar.gz'
assert archive.stat().st_size == snapshot['archive_bytes'] <= 134217728
assert hashlib.sha256(archive.read_bytes()).hexdigest() == snapshot['archive_sha256']
key = 'relh-sugarscape-evidence-20261017/brearcliffe-final-recovered-cohort-20261020-001/paper-pair15-50.tar.gz'
readback = root / 'storage-paper-pair15-50.tar.gz'
assert not readback.exists()
for direction, paths in [('upload', [str(archive), key]), ('download', [key, str(readback)])]:
    with (root / f'cohort-storage-{direction}.json').open('x') as log:
        subprocess.run(['autor', 'storage', 'cp', *paths, '--json'], stdout=log, check=True, timeout=600)
assert readback.stat().st_size == snapshot['archive_bytes']
assert hashlib.sha256(readback.read_bytes()).hexdigest() == snapshot['archive_sha256']
with tarfile.open(readback) as bundle:
    members = bundle.getmembers()
    assert all(m.isfile() for m in members) and len({m.name for m in members}) == len(members)
    hashes = {m.name: {'bytes': m.size, 'sha256': hashlib.sha256(bundle.extractfile(m).read()).hexdigest()} for m in members}
assert hashes == snapshot['files']
(root / 'storage-readback.json').write_text(json.dumps({'storage_object': key, 'archive_bytes': snapshot['archive_bytes'], 'archive_sha256': snapshot['archive_sha256'], 'fresh_download_exact': True, 'snapshot_run_members_exact': True, 'member_sha256': hashes}, indent=2) + '\n')
(root / 'synthesis-provenance.json').write_text(json.dumps({'source_sha256': {Path(name).name: digest for name, digest in plan['source_sha256'].items()}, 'repository_head': plan['repository_head'], 'original_final_cohort_inputs': 6, 'recovery_final_cohort_inputs': 44, 'native_methods_changed': False, 'scope': 'Automatic artifact assembly and arithmetic only. Whole-method verdict and publication review remain required.'}, indent=2) + '\n')
homogeneous = evidence / 'brearcliffe-paper-homogeneous-claims-001'
tools = evidence.parent / 'sugarscape-replication-tools'
env = {**os.environ, 'R_LIBS_USER': str(tools / 'R-library')}
commands = [
    [sys.executable, str(root / 'publish.py')],
    [str(tools / 'pdf-analysis-001/bin/python'), str(homogeneous / 'analyze.py'), str(repo), str(root / 'union-audit/audit.json')],
    ['/opt/homebrew/bin/Rscript', '--vanilla', str(homogeneous / 'verify.R'), str(homogeneous), str(repo), str(root / 'union-audit/audit.json')],
    [sys.executable, str(repo / 'compare_parameter_interpretations.py'), str(repo / 'results'), str(root / 'parameter-comparison.json')],
    ['/opt/homebrew/bin/Rscript', '--vanilla', str(repo / 'verify_parameter_interpretations.R'), str(repo / 'results'), str(root / 'parameter-comparison.json'), str(root / 'parameter-r-verification.json')],
]
for index, command in enumerate(commands):
    with (root / f'synthesis-{index}.log').open('x') as log:
        subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, env=env, timeout=900, check=True)
(root / 'synthesis-terminal.json').write_text(json.dumps({'exit_code': 0, 'audited_inputs': 1600, 'parameter_pairings': 16, 'homogeneous_contrasts': 28, 'publication_and_method_verdict_review_pending': True}, indent=2) + '\n')
