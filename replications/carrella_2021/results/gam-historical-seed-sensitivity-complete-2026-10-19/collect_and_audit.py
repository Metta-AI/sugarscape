"""Wait for the existing bounded batch and audit all ten preselected fitting seeds."""
from pathlib import Path
import csv
import hashlib
import json
import os
import subprocess
import tarfile
import time

root = Path(__file__).resolve().parent
base = root.parent
node = 'relh-sugarscape-carrella-r405-cpu2-20261019-v1'
command = 'cmd-fwscs'
collector = base / 'storage-handoff-20261017-001/carrella-seeds-collector-recovery-20261019-1858'
deadline = time.monotonic() + 3600
with (root / 'observations.jsonl').open('x') as observations:
    while True:
        states = json.loads(subprocess.check_output(['autor','ps',node,'--json'],timeout=30))
        state = next(x for x in states['items'] if x['command_id'] == command)
        observations.write(json.dumps(state)+'\n'); observations.flush()
        if state['state'] == 'exited':
            assert state['exit_code'] == 0
            break
        assert state['state'] == 'running' and time.monotonic() < deadline
        time.sleep(30)
    while True:
        status_path = collector / 'results.tar.gz.status.json'
        if status_path.exists():
            status = json.loads(status_path.read_text())
            if status['status'] == 'complete':
                break
            assert status['status'] == 'running'
        assert time.monotonic() < deadline
        time.sleep(10)
intent = json.loads((collector/'results.tar.gz.intent.json').read_text())
receipt = intent['receipt']
assert status['bytes_transferred'] == receipt['bytes']
archive = root/'results.tar.gz'
p = subprocess.run(['autor','storage','cp','relh-sugarscape-evidence-20261017/'+intent['destination'],str(archive),'--json'],capture_output=True,text=True,timeout=180)
(root/'download.json').write_text(json.dumps({'exit_code':p.returncode,'stdout':p.stdout,'stderr':p.stderr},indent=2)+'\n')
assert p.returncode == 0
assert archive.stat().st_size == receipt['bytes'] and hashlib.sha256(archive.read_bytes()).hexdigest() == receipt['sha256']
native = root/'native'; native.mkdir()
with tarfile.open(archive) as tar:
    members = tar.getmembers()
    assert len({m.name for m in members}) == len(members)
    assert all((m.isfile() or m.isdir()) and not Path(m.name).is_absolute() and '..' not in Path(m.name).parts for m in members)
    hashes = {m.name:hashlib.sha256(tar.extractfile(m).read()).hexdigest() for m in members if m.isfile()}
    assert len(hashes) == 127
    tar.extractall(native,filter='data')
for name,digest in hashes.items():
    assert hashlib.sha256((native/name).read_bytes()).hexdigest() == digest
payload = base/'carrella-gam-historical-seeds-001/payload'
frozen = [name for name in hashes if (payload/name).is_file()]
assert len(frozen) == 16
for name in frozen:
    assert (native/name).read_bytes() == (payload/name).read_bytes()
assert json.loads((native/'terminal.json').read_text())['exit_code'] == 0
study = base.parent/'sugarscape-carrella/replications/carrella_2021'
qualified_source = (study/'replay_gam_folds.R').read_bytes()
for seed in range(1,10):
    seed_root = native/f'seed-{seed:02d}'
    assert json.loads((seed_root/'terminal.json').read_text())['exit_code'] == 0
    assert (seed_root/'replay.R').read_bytes().replace(f'set.seed({seed})'.encode(),b'set.seed(0)') == qualified_source
(root/'readback.json').write_text(json.dumps({'receipt':receipt,'members':hashes,'frozen_payload_members_exact':frozen,'source_reversal_exact':True,'source_sha256':hashlib.sha256(qualified_source).hexdigest(),'completed_seeds':list(range(1,10))},indent=2)+'\n')
env = dict(os.environ,R_LIBS_USER=str(base.parent/'sugarscape-replication-tools/R-library'))
seed0 = base/'carrella-gam-historical-full-readback-001/native/run'
metrics = []
for seed in range(10):
    run = seed0 if seed == 0 else native/f'seed-{seed:02d}/run'
    output = root/f'audit-{seed:02d}'
    cmd = ['/opt/homebrew/bin/Rscript','--vanilla',str(study/'audit_replayed_gam.R'),str(native/'inputs'),str(run),str(study/'published_table8.json'),str(output)]
    p = subprocess.run(cmd,capture_output=True,text=True,env=env,timeout=120)
    (root/f'audit-{seed:02d}-command.json').write_text(json.dumps({'command':cmd,'exit_code':p.returncode,'stdout':p.stdout,'stderr':p.stderr},indent=2)+'\n')
    assert p.returncode == 0, p.stderr
    with (output/'metrics.csv').open() as stream:
        metrics.extend({'seed':seed,**row} for row in csv.DictReader(stream))
cmd = ['/opt/homebrew/bin/Rscript','--vanilla',str(root/'compare_seed0.R'),str(seed0),str(native),str(root/'seed0-comparison.json')]
p = subprocess.run(cmd,capture_output=True,text=True,env=env,timeout=120)
(root/'comparison-command.json').write_text(json.dumps({'command':cmd,'exit_code':p.returncode,'stdout':p.stdout,'stderr':p.stderr},indent=2)+'\n'); assert p.returncode == 0,p.stderr
parameters = sorted({r['parameter'] for r in metrics})
assert len(metrics) == 50 and len(parameters) == 5
summary = []
for parameter in parameters:
    selected = [r for r in metrics if r['parameter'] == parameter]
    assert {r['seed'] for r in selected} == set(range(10))
    summary.append({'parameter':parameter,'published':float(selected[0]['published']),'matching_seeds':[r['seed'] for r in selected if r['matches_printed_precision']=='TRUE'],'ranges':{name:{'minimum':min(float(r[name]) for r in selected),'maximum':max(float(r[name]) for r in selected)} for name in ['performance','coverage','interval_width']}})
(root/'sensitivity-summary.json').write_text(json.dumps({'seeds':list(range(10)),'parameters':summary,'metrics':metrics,'scope':'All ten preselected fitting seeds, historical runtime and fixed folds. Observed ranges are not confidence intervals and do not identify the author environment or prove a negative replication.'},indent=2)+'\n')
(root/'analysis-terminal.json').write_text(json.dumps({'exit_code':0,'audited_seeds':10,'scope':'Full seed-sensitivity audit complete; publication review remains.'},indent=2)+'\n')
print(json.dumps(summary),flush=True)
