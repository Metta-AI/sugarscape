"""Run a bounded, disjoint prefix of an audited remaining ensemble manifest."""

import argparse
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
import csv
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('prepared', type=Path)
parser.add_argument('remaining_csv', type=Path)
parser.add_argument('runtime_assets', type=Path)
parser.add_argument('netlogo_app', type=Path)
parser.add_argument('new_output', type=Path)
parser.add_argument('--java', required=True)
parser.add_argument('--interpretation', choices=['released-code', 'paper-table'], required=True)
parser.add_argument('--workers', type=int, required=True)
parser.add_argument('--max-inputs', type=int, required=True)
parser.add_argument('--wall-seconds', type=int, required=True)
parser.add_argument('--per-run-seconds', type=int, default=1800)
args = parser.parse_args()
assert 1 <= args.workers <= 8
assert 1 <= args.max_inputs <= 800
assert 1 <= args.per_run_seconds <= 3600
assert args.per_run_seconds + 30 <= args.wall_seconds <= 86400
manifest = args.prepared / 'manifest.csv'
summary = json.loads((args.prepared / 'summary.json').read_text())
assert hashlib.sha256(manifest.read_bytes()).hexdigest() == summary['manifest_sha256']
with manifest.open() as file:
    expected = {row['run_id']: row for row in csv.DictReader(file)}
with args.remaining_csv.open() as file:
    remaining = list(csv.DictReader(file))
assert len({r['run_id'] for r in remaining}) == len(remaining)
assert all(row == expected[row['run_id']] for row in remaining)
selected = [r for r in remaining if r['interpretation'] == args.interpretation][:args.max_inputs]
assert selected
args.new_output.mkdir()
output = args.new_output.resolve()
(output / 'runs').mkdir()
(output / 'logs').mkdir()
plan = {'manifest_sha256': summary['manifest_sha256'],
        'remaining_csv_sha256': hashlib.sha256(args.remaining_csv.read_bytes()).hexdigest(),
        'input_ids': [r['run_id'] for r in selected], 'workers': args.workers,
        'per_run_seconds': args.per_run_seconds, 'wall_seconds': args.wall_seconds,
        'interpretation': args.interpretation}
(output / 'plan.json').write_text(json.dumps(plan, indent=2) + '\n')
started = time.monotonic()
deadline = started + args.wall_seconds


def execute(row):
    run_id = row['run_id']
    destination = output / 'runs' / run_id
    command = [sys.executable, str(Path(__file__).with_name('run_ensemble_input.py').resolve()),
               str(args.prepared.resolve()), run_id, str(args.runtime_assets.resolve()),
               str(args.netlogo_app.resolve()), str(destination), '--java', args.java,
               '--timeout-seconds', str(args.per_run_seconds)]
    (output / 'logs' / f'{run_id}-command.json').write_text(json.dumps(command, indent=2) + '\n')
    before = time.monotonic()
    with (output / 'logs' / f'{run_id}.log').open('x') as log:
        process = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT,
                                 timeout=args.per_run_seconds + 30)
    receipt = {'run_id': run_id, 'exit_code': process.returncode, 'elapsed_seconds': time.monotonic() - before}
    (output / 'logs' / f'{run_id}-terminal.json').write_text(json.dumps(receipt, indent=2) + '\n')
    return receipt


next_input = 0
receipts = []
failed = False
with ThreadPoolExecutor(max_workers=args.workers) as executor:
    pending = set()
    while pending or next_input < len(selected):
        while (not failed and len(pending) < args.workers and next_input < len(selected)
               and deadline - time.monotonic() >= args.per_run_seconds + 30):
            pending.add(executor.submit(execute, selected[next_input]))
            next_input += 1
        if not pending:
            break
        finished, pending = wait(pending, return_when=FIRST_COMPLETED)
        for future in finished:
            receipt = future.result()
            receipts.append(receipt)
            with (output / 'attempts.jsonl').open('a') as file:
                file.write(json.dumps(receipt) + '\n')
            failed = failed or receipt['exit_code'] != 0
            print(json.dumps(receipt), flush=True)
terminal = {'exit_code': 1 if failed else 0, 'attempted_inputs': next_input,
            'successful_inputs': sum(r['exit_code'] == 0 for r in receipts),
            'unstarted_inputs': len(selected) - next_input, 'elapsed_seconds': time.monotonic() - started,
            'scope': 'Bounded manifest prefix; independent trajectory audit required before coverage credit.'}
(output / 'terminal.json').write_text(json.dumps(terminal, indent=2) + '\n')
print(json.dumps(terminal))
assert not failed, 'One or more inputs failed; preserved receipts and partial trajectories require inspection.'
