"""Join the primary Table 8 discrepancies to retained, same-size estimator controls."""

import argparse
import csv
from decimal import Decimal, ROUND_HALF_EVEN
import hashlib
import json
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('new_output', type=Path)
args = parser.parse_args()
root = Path(__file__).resolve().parent / 'results'
paths = {
    'coverage': root / 'table8-coverage-2026-10-17/coverage.json',
    'paired': root / 'estimator-comparison-complete-2026-10-19/comparison.csv',
    'seed': root / 'sabc1d-seed-sensitivity-2026-10-19/summary.json',
    'seed5000': root / 'sabc1d5000-seed-sensitivity-complete-2026-10-19/summary.json',
    'gam': root / 'gam-parser-control-complete-2026-10-17/parser-comparison.json',
    'forest': root / 'notebook-rf-parser-control-completed-2026-10-17/audit.json',
}
pins = {str(p.relative_to(root.parent)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths.values()}
coverage = json.loads(paths['coverage'].read_text())['cells']
with paths['paired'].open() as file:
    paired = {(int(r['size']), r['method'], r['parameter']): r for r in csv.DictReader(file)}
assert len(coverage) == len(paired) == 90
controls = {}
for kind, size, method, field in [
    ('seed', 1250, 'Semi-automatic ABC 1D', 'summary'),
    ('seed5000', 5000, 'Semi-automatic ABC 1D', 'summary'),
    ('gam', 1250, 'GAM', 'comparison'),
    ('forest', 5000, 'Quantile Random Forest', 'comparison'),
]:
    for item in json.loads(paths[kind].read_text())[field]:
        controls[(size, method, item['parameter'])] = (kind, item)
rows = []
family_counts = {}
for cell in coverage:
    key = (cell['size'], cell['method'], cell['parameter'])
    pair = paired[key]
    assert pair['published'] == cell['published']
    if cell['status'] == 'not_reported':
        assert pair['status'] == 'not_reported'
        continue
    score = float(pair['author_rerun'])
    assert abs(score - cell['measured']) < 1e-12
    evidence = root.parent.parent.parent / cell['evidence']
    assert hashlib.sha256(evidence.read_bytes()).hexdigest() == cell['evidence_sha256']
    pins[cell['evidence']] = cell['evidence_sha256']
    printed_match = Decimal(str(score)).quantize(Decimal('0.001'), rounding=ROUND_HALF_EVEN) == Decimal(cell['published'])
    assert printed_match == cell['matches_printed_precision']
    if printed_match:
        continue
    family_counts[cell['method']] = family_counts.get(cell['method'], 0) + 1
    row = {'size': cell['size'], 'method': cell['method'], 'parameter': cell['parameter'],
           'published': cell['published'], 'primary_score': score,
           'primary_minus_published': score - float(cell['published']),
           'primary_evidence': cell['evidence'], 'selected_control_status': 'no-selected-same-size-control'}
    if key in controls:
        kind, control = controls[key]
        row['selected_control'] = kind
        row['control_evidence'] = str(paths[kind].relative_to(root.parent))
        if kind in ('seed', 'seed5000'):
            assert abs(control['primary_seed_zero'] - score) < 1e-12
            row['observed_seed_range'] = [control['minimum'], control['maximum']]
            row['published_within_observed_seed_range'] = control['minimum'] <= float(cell['published']) <= control['maximum']
            assert row['published_within_observed_seed_range'] == control['published_within_observed_range']
            row['selected_control_status'] = 'seed-range-compared-not-a-confidence-interval'
        else:
            if kind == 'gam':
                assert abs(control['primary'] - score) < 1e-12
                alternative = control['parser_control']
            else:
                assert abs(control['published'] - float(cell['published'])) < 1e-12
                alternative = control['performance']
            row['control_score'] = alternative
            row['control_matches_printed_precision'] = Decimal(str(alternative)).quantize(Decimal('0.001'), rounding=ROUND_HALF_EVEN) == Decimal(cell['published'])
            row['selected_control_status'] = 'alternative-score-compared-primary-unchanged'
    rows.append(row)
assert len(rows) == 37
report = {'primary_matches': 38, 'primary_discrepancies': 37, 'unreported_cells': 15,
          'discrepancies_by_method': family_counts,
          'discrepancies_with_selected_controls': sum('selected_control' in r for r in rows),
          'rows': rows, 'evidence_sha256': pins,
          'limits': ['Only the four named same-size aggregate controls are joined here; other diagnostics remain in their original results.',
                     'A seed-range inclusion does not identify the historical RNG or establish agreement.',
                     'A secondary control match does not replace the primary score or establish causation.',
                     'Point-fit historical-runtime diagnostics are excluded from aggregate score comparisons.',
                     'No published-score discrepancy is reclassified as a validated negative or a new primary match.']}
args.new_output.mkdir()
(args.new_output / 'reconciliation.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps({k: v for k, v in report.items() if k not in ['rows', 'evidence_sha256', 'limits']}))
