from pathlib import Path
import hashlib
import json

root = Path(__file__).resolve().parent
repo = Path('/Users/relh/Code/workspace/sugarscape-brearcliffe/replications/brearcliffe_2020')
released_path = repo / 'results/rule-m-q-complete-cohort-2026-10-19/cohort-summary.json'
paper_path = root / 'cohort/summary.json'
released = json.loads(released_path.read_text())
paper = json.loads(paper_path.read_text())
assert released['pair_index'] == paper['pair_index'] == 2
assert released['manifest_sha256'] == paper['manifest_sha256']
assert released['runs'] == paper['runs'] == 50
pairs = []
for repeat in range(50):
    released_id = f'released-code-pair-02-repeat-{repeat:02d}'
    paper_id = f'paper-table-pair-02-repeat-{repeat:02d}'
    a = released['trajectory_sha256'][released_id]
    b = paper['trajectory_sha256'][paper_id]
    pairs.append({'released_id': released_id, 'paper_id': paper_id, 'released_sha256': a, 'paper_sha256': b, 'identical': a == b})
report = {
    'released_summary_sha256': hashlib.sha256(released_path.read_bytes()).hexdigest(),
    'paper_summary_sha256': hashlib.sha256(paper_path.read_bytes()).hexdigest(),
    'paired_inputs': len(pairs),
    'identical_full_trajectories': sum(x['identical'] for x in pairs),
    'pairs': pairs,
    'scope': 'Paired frozen-seed trajectory hashes across the two parameter interpretations. This does not identify the historical settings or establish paper agreement.',
}
(root / 'paired-interpretations.json').write_text(json.dumps(report, indent=2) + '\n')
print({k: v for k, v in report.items() if k != 'pairs'})
