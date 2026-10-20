"""Assign audited remaining inputs while excluding explicit reservations."""

import argparse
import csv
import hashlib
import json
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('prepared', type=Path)
parser.add_argument('remaining_csv', type=Path)
parser.add_argument('new_output', type=Path)
parser.add_argument('--reserved-plan', type=Path, action='append', default=[])
parser.add_argument('--interpretation', required=True, choices=['released-code', 'paper-table'])
parser.add_argument('--pair-index', type=int, choices=range(16))
parser.add_argument('--max-inputs', required=True, type=int)
args = parser.parse_args()
assert 1 <= args.max_inputs <= 800
manifest = args.prepared / 'manifest.csv'
manifest_hash = hashlib.sha256(manifest.read_bytes()).hexdigest()
assert manifest_hash == json.loads((args.prepared / 'summary.json').read_text())['manifest_sha256']
with manifest.open() as file:
    original = list(csv.DictReader(file))
expected = {r['run_id']: r for r in original}
assert len(expected) == len(original) == 1600
with args.remaining_csv.open() as file:
    remaining = list(csv.DictReader(file))
assert len({r['run_id'] for r in remaining}) == len(remaining)
assert all(row == expected[row['run_id']] for row in remaining)
reserved = set()
reservation_sources = []
for path in args.reserved_plan:
    plan = json.loads(path.read_text())
    assert plan['manifest_sha256'] == manifest_hash
    ids = plan['input_ids']
    assert len(set(ids)) == len(ids)
    assert set(ids) <= expected.keys()
    assert not reserved.intersection(ids), 'Existing reservations overlap; resolve ownership before assigning work.'
    reserved.update(ids)
    reservation_sources.append({'path': str(path.resolve()), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
selected = [row for row in remaining if row['run_id'] not in reserved
            and row['interpretation'] == args.interpretation
            and (args.pair_index is None or int(row['pair_index']) == args.pair_index)][:args.max_inputs]
assert selected, 'No unreserved matching inputs remain.'
args.new_output.mkdir()
with (args.new_output / 'assignment.csv').open('x', newline='') as file:
    writer = csv.DictWriter(file, fieldnames=list(original[0]))
    writer.writeheader()
    writer.writerows(selected)
plan = {'manifest_sha256': manifest_hash,
        'remaining_csv_sha256': hashlib.sha256(args.remaining_csv.read_bytes()).hexdigest(),
        'reservation_sources': reservation_sources, 'excluded_reserved_inputs': sorted(reserved),
        'input_ids': [row['run_id'] for row in selected],
        'assignment_sha256': hashlib.sha256((args.new_output / 'assignment.csv').read_bytes()).hexdigest(),
        'scope': 'Reserved assignment only; not execution or completion evidence.'}
(args.new_output / 'plan.json').write_text(json.dumps(plan, indent=2) + '\n')
print(json.dumps({'assigned_inputs': len(selected), 'excluded_reserved_inputs': len(reserved),
                  'assignment_sha256': plan['assignment_sha256']}))
