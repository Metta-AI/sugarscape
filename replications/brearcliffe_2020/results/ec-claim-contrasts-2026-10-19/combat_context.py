from pathlib import Path
import gzip
import hashlib
import json

root = Path(__file__).resolve().parent
repo = Path('/Users/relh/Code/workspace/sugarscape-brearcliffe/replications/brearcliffe_2020/results')
contrasts = json.loads((root / 'contrasts.json').read_bytes())
records = []
pins = {}
for name in ['rule-m-ec', 'ec-rule-m']:
    source = repo / (name + '-complete-cohort-2026-10-19') / 'curve-comparison.json.gz'
    pins[str(source)] = hashlib.sha256(source.read_bytes()).hexdigest()
    comparison = json.loads(gzip.decompress(source.read_bytes()))
    endpoints = [max([row for row in comparison['records'] if row['metric'] == metric], key=lambda row: row['column'])
                 for metric in ['combat-agent-a-die', 'combat-agent-b-die']]
    assert all(row['signed_range_separation'] == 0 for row in endpoints)
    record = next(row for row in contrasts['records'] if row['pairing'] == name and row['metric'] == 'combat')
    records.append({'pairing': name, 'ec_combat_mean': record['ec_endpoint_mean'],
                    'rule_m_combat_mean': record['opponent_endpoint_mean'],
                    'ec_minus_rule_m_mean': record['paired_endpoint_mean'],
                    'relative_difference_percent_of_rule_m': 100 * record['paired_endpoint_mean'] / record['opponent_endpoint_mean'],
                    'paper_endpoint_records': endpoints})
report = {'records': records, 'source_sha256': pins,
          'contrasts_sha256': hashlib.sha256((root / 'contrasts.json').read_bytes()).hexdigest(),
          'scope': 'The four native endpoint ranges overlap their corresponding corrected Figure6 raster ranges. Relative size provides context for unquantified prose, not a statistical equivalence test or paper-negative verdict.'}
(root / 'combat-context.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps([{key: value for key, value in row.items() if key != 'paper_endpoint_records'} for row in records]))
