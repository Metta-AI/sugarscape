"""One-time qualified handoff of this task's owned local Bentham producer."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
import psutil

base = Path('/Users/relh/Code/workspace/sugarscape-replication-evidence')
root = base / 'blueprints-bentham-parallel-001'
qualification = base / 'blueprints-bentham-parallel-qualification-001'
source = base / 'blueprints-2024-resumed-benthamHalfLookaheadBinary-005'
expected_hash = 'd191dbe7daa4e1aafd807d727c1eee48288c08436c0104f822b79c0b985bbebb'
assert not (root / 'stop-receipt.json').exists()
assert json.loads((root / 'staging.json').read_text())['exit_code'] == 0
assert (qualification / 'terminal/exit-code.txt').read_text().strip() == '0'
audit = json.loads((qualification / 'audit/audit.json').read_text())
assert audit['runs'] == 1 and audit['observations'] == 5001
assert audit['results'][0]['trajectory_sha256'] == expected_hash
parent = psutil.Process(18256)
command = parent.cmdline()
assert command[1] == '/Users/relh/Code/workspace/sugarscape-blueprints/replications/blueprints_2024/run_batch.py'
assert command[4] == 'benthamHalfLookaheadBinary' and command[5] == str(source)
assert command[-4:] == ['--start', '20', '--stop', '500']
before = {'parent': {'pid': parent.pid, 'created': parent.create_time(), 'command': command}, 'children': []}
parent.suspend()
terminated = False
try:
    children = parent.children(recursive=True)
    for child in children:
        child_command = child.cmdline()
        assert any(str(source) in argument for argument in child_command), child_command
        assert any(argument.endswith('/run.py') or argument.endswith('/sugarscape.py') for argument in child_command), child_command
        before['children'].append({'pid': child.pid, 'created': child.create_time(), 'command': child_command})
    (root / 'processes-before-stop.json').write_text(json.dumps(before, indent=2) + '\n')
    for child in reversed(children):
        child.terminate()
    parent.kill()
    terminated = True
finally:
    if not terminated:
        parent.resume()
gone, alive = psutil.wait_procs([parent, *children], timeout=15)
assert not alive, [(p.pid, p.cmdline()) for p in alive]
raw = (source / 'completed.jsonl').read_bytes()
assert raw.endswith(b'\n')
rows = [json.loads(line) for line in raw.splitlines()]
(root / 'local-completed.jsonl').write_bytes(raw)
completed_seeds = {row['seed'] for row in rows}
partials = {}
for directory in source.glob('seed-*'):
    if int(directory.name.removeprefix('seed-')) not in completed_seeds:
        partials[directory.name] = {p.name: {'bytes': p.stat().st_size, 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()} for p in directory.iterdir() if p.is_file()}
(root / 'preserved-partial-files.json').write_text(json.dumps({'source': str(source), 'files': partials}, indent=2) + '\n')
receipt = {'local_parent_pid': 18256, 'stopped_at': datetime.now(timezone.utc).isoformat(), 'native_process_ids': [p.pid for p in children], 'terminal_process_ids': sorted(p.pid for p in gone), 'completed_ledger_sha256': hashlib.sha256(raw).hexdigest(), 'partial_attempt_preserved': True}
stop_bytes = (json.dumps(receipt, indent=2) + '\n').encode()
(root / 'stop-receipt.json').write_bytes(stop_bytes)
end = 20 + len(rows)
plan = {'model': 'benthamHalfLookaheadBinary', 'local_completed_start': 20, 'completed_prefix_end': end, 'remaining_indices': list(range(end, 500)), 'workers': 32, 'per_input_limit_seconds': 3600, 'stop_receipt_sha256': hashlib.sha256(stop_bytes).hexdigest(), 'qualification_trajectory_sha256': expected_hash}
(root / 'plan.json').write_text(json.dumps(plan, indent=2) + '\n')
print(json.dumps({'stopped_processes': receipt['terminal_process_ids'], 'completed_prefix_end': end, 'remaining_inputs': len(plan['remaining_indices']), 'preserved_partial_directories': list(partials)}))
