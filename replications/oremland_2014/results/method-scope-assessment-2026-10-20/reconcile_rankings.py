"""Reconcile all complete native ranking cases without double-counting snapshots."""
from pathlib import Path
import hashlib
import json
import sys

root = Path(sys.argv[1])
output = Path(sys.argv[2])
assert not output.exists()
rows = []
for folder in ['ranking-prefix-2026-10-18', 'ranking-extension-2026-10-18', 'ranking-recovery-2026-10-18']:
    for path in sorted((root / 'results' / folder).rglob('audit.json')):
        audit = json.loads(path.read_bytes())
        assert audit['policies'] == 100 and audit['clock_phases'] == [0, 4]
        assert audit['validated_jsonl_lines'] == 2 * audit['complete_native_runs']
        rows.append({'model': audit['model'], 'width': audit['width'],
                     'native_runs': audit['complete_native_runs'],
                     'evidence': str(path.relative_to(root)),
                     'sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
assert len(rows) == len({row['model'] for row in rows}) == 12
reduced = sum(row['native_runs'] for row in rows if row['width'] != 50)
full = sum(row['native_runs'] for row in rows if row['width'] == 50)
assert reduced == 2538400 and full == 10000
output.write_text(json.dumps({'reduced_native_runs': reduced, 'independent_full_native_runs': full,
                             'cases': rows, 'scope': 'Reconciliation of complete native audits; not a new raw replay or numerical agreement verdict.'}, indent=2) + '\n')
print(json.dumps({'reduced': reduced, 'full': full, 'cases': len(rows)}))
