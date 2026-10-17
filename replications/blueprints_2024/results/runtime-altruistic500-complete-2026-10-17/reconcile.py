from pathlib import Path
from collections import Counter
import hashlib
import json
import zipfile

root = Path('/Users/relh/Code/workspace/sugarscape-replication-evidence')
paths = [root / 'blueprints-runtime-altruistic500-pilot-final-audit-001/audit.json',
         root / 'blueprints-runtime-altruistic500-complete-audit-001/audit.json']
audits = [json.loads(path.read_text()) for path in paths]
assert all(a['complete_interval'] and a['steps'] == 500 and a['model'] == 'altruisticHalfLookaheadBinary' for a in audits)
assert [a['ordinal_interval'] for a in audits] == [[0, 1], [1, 100]]
rows = [row for audit in audits for row in audit['results']]
with zipfile.ZipFile(root / 'papers/blueprints-runtimes.zip') as archive:
    expected = sorted(name for name in archive.namelist() if name.startswith('500-altruisticHalfLookaheadBinary'))
assert len(rows) == len(expected) == 100
assert [row['entry'] for row in rows] == expected
assert len({row['seed'] for row in rows}) == 100
report = {'complete_group': True, 'validated_runs': 100, 'steps': 500,
          'model': 'altruisticHalfLookaheadBinary', 'observations': sum(row['observations'] for row in rows),
          'counts': dict(Counter(row['outcome'] for row in rows)),
          'equal_to_initial_population': sum(row['final_population'] == 250 for row in rows),
          'audit_sha256': {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in paths},
          'scope': 'Complete deposited100seed group, pilot counted once. No500seed Table6 verdict.', 'results': rows}
Path(__file__).with_name('reconciliation.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps({k:v for k,v in report.items() if k != 'results'}))
