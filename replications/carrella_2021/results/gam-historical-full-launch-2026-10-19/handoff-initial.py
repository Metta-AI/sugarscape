"""Bounded task-specific handoff: qualify, provision pinned runtime, preserve evidence."""
from pathlib import Path
import hashlib
import json
import subprocess
import time

root = Path(__file__).resolve().parent
base = root.parent
qualification = base / 'carrella-gam-full-runtime-001'
preparation = base / 'carrella-gam-historical-full-preparation-001'
node = 'relh-sugarscape-carrella-r405-cpu2-20261019-v1'
remote = '/root/sugarscape/' + root.name
protocol = json.loads((preparation / 'protocol.json').read_text())
(root / 'handoff-start.json').write_text(json.dumps({'node': node, 'unix': time.time(), 'qualification_wait_seconds': 1900}, indent=2) + '\n')

def call(name, args, timeout=90):
    result = subprocess.run(args, capture_output=True, text=True, timeout=timeout)
    (root / (name + '.json')).write_text(json.dumps({'command': args, 'exit_code': result.returncode, 'stdout': result.stdout, 'stderr': result.stderr}, indent=2) + '\n')
    assert result.returncode == 0, name
    return json.loads(result.stdout)

deadline = time.monotonic() + 1900
while not (qualification / 'current-terminal.json').is_file():
    assert time.monotonic() < deadline, 'Qualification observation expired; no historical run launched'
    time.sleep(20)
assert json.loads((qualification / 'current-terminal.json').read_text())['exit_code'] == 0
assert (qualification / 'current/complete.txt').read_text().strip() == 'All 18750 predictions and interval bounds and five final random states match exactly.'
for entry in protocol['files'].values():
    path = Path(entry['source'])
    assert path.stat().st_size == entry['bytes']
    assert hashlib.sha256(path.read_bytes()).hexdigest() == entry['sha256']
assert hashlib.sha256((preparation / 'payload.tar.gz').read_bytes()).hexdigest() == protocol['payload_sha256']
check = '''args<-commandArgs(TRUE); n<-0L
for(i in 1:5){a<-readRDS(file.path(args[1],paste0("fold-",i,".rds")));b<-readRDS(file.path(args[2],paste0("fold-",i,".rds")))
for(f in c("predictions","lows","highs")){x<-as.matrix(a$result[[f]]);y<-as.matrix(b[[f]]);stopifnot(identical(dim(x),dim(y)),identical(colnames(x),colnames(y)),identical(as.numeric(x),as.numeric(y)));n<-n+length(x)}
stopifnot(identical(a$random_state,b$random_state))};stopifnot(n==18750L);cat("18750 exact numeric values and five exact final RNG states\\n")'''
source = Path(protocol['files']['inputs/fold-1.rds']['source']).parent
result = subprocess.run(['/opt/homebrew/bin/Rscript', '--vanilla', '-e', check, str(source), str(qualification / 'current')], capture_output=True, text=True, timeout=60)
(root / 'qualification-readback.json').write_text(json.dumps({'script': check, 'exit_code': result.returncode, 'stdout': result.stdout, 'stderr': result.stderr}, indent=2) + '\n')
assert result.returncode == 0
print('Full qualification and fresh readback pass; provisioning pinned historical runtime', flush=True)
created = call('create-node', ['autor', 'node', 'create', '--name', node, '--chip', 'cpu-2', '--image', protocol['image'], '--max-wait', '10m', '--json'])
started = time.monotonic()
while True:
    state = call('node-state', ['autor', 'node', 'get', node, '--json'])
    if state['status'] == 'running':
        break
    assert state['status'] in ('queued', 'provisioning') and time.monotonic() - started < 900
    time.sleep(20)
rate = state['rate']
if rate['node_per_min_usd_micros'] > 3000 or rate['idle_window_minutes'] > 15:
    call('rate-rejection-stop', ['autor', 'node', 'stop', node, '--json'])
    raise RuntimeError('New node rate exceeded prospective price gate; owned node stopped without running fits')
assert rate['node_per_min_usd_micros'] * (120 + 20 + 15) <= 3000000
result = call('mkdir', ['autor', 'run', node, '--timeout', '60', '--json', '--', 'mkdir', '-p', remote])
assert result['exit_code'] == 0
call('payload-upload', ['autor', 'cp', str(preparation / 'payload.tar.gz'), node + ':' + remote + '/payload.tar.gz', '--json'], 180)
call('runner-upload', ['autor', 'cp', str(root / 'run.sh'), node + ':' + remote + '/run.sh', '--json'], 180)
submission = call('submission', ['autor', 'run', node, '--detach', '--timeout', '60', '--json', '--', 'timeout', '--kill-after=10', '7500', 'bash', remote + '/run.sh'])
print(json.dumps({'node': node, 'command': submission['command_id']}), flush=True)
collector = base / 'storage-handoff-20261017-001/collect_storage_api_bounded.py'
with (root / 'collector.log').open('x') as log:
    result = subprocess.run(['/Users/relh/Code/workspace/sugarscape-replications/.venv/bin/python', str(collector), node, submission['command_id'], root.name, '--terminal-file', remote + '/results.tar.gz', '--seconds', '7800', '--max-bytes', str(50 * 1024**2)], stdout=log, stderr=subprocess.STDOUT, timeout=8000)
(root / 'handoff-terminal.json').write_text(json.dumps({'exit_code': result.returncode}, indent=2) + '\n')
assert result.returncode == 0
