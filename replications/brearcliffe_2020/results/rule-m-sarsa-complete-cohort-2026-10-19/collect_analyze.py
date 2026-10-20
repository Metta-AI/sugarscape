from pathlib import Path
import json
import os
import subprocess
import sys
import time

root = Path(__file__).resolve().parent
node = 'relh-sugarscape-runtime-memory-cpu8-20261018-v1'
repo = Path('/Users/relh/Code/workspace/sugarscape-brearcliffe/replications/brearcliffe_2020')
prepared = root.parent / 'brearcliffe-ensemble-preparation-001'
assert json.loads((root / 'terminal.json').read_text())['exit_code'] == 0
for name in ('snapshot.json', 'pair03-50.tar.gz'):
    result = subprocess.run(['autor', 'cp', f'{node}:/root/sugarscape/{root.name}/{name}', str(root / name), '--json'], capture_output=True, text=True, timeout=180)
    (root / f'{name}-download.json').write_text(json.dumps({'exit_code': result.returncode, 'stdout': result.stdout, 'stderr': result.stderr}, indent=2) + '\n')
    assert result.returncode == 0
with (root / 'readback.log').open('w') as stream:
    subprocess.run([sys.executable, str(root / 'readback.py')], stdout=stream, stderr=subprocess.STDOUT, timeout=300, check=True)
env = dict(os.environ, R_LIBS_USER='/Users/relh/Code/workspace/sugarscape-replication-tools/R-library')
with (root / 'r-validation.log').open('w') as stream:
    subprocess.run(['/opt/homebrew/bin/Rscript', '--vanilla', str(repo / 'verify_cohort.R'), str(prepared), str(root / 'union-audit/audit.json'), str(root / 'cohort'), str(root / 'r-validation.json')], env=env, stdout=stream, stderr=subprocess.STDOUT, timeout=300, check=True)
with (root / 'comparison.log').open('w') as stream:
    subprocess.run([sys.executable, str(repo / 'compare_curves.py'), str(root / 'cohort'), str(repo / 'results/full-curve-digitization-2026-10-19/metric-curves.json.gz'), str(root / 'comparison')], stdout=stream, stderr=subprocess.STDOUT, timeout=120, check=True)
(root / 'analysis-terminal.json').write_text(json.dumps({'exit_code': 0, 'cohort': 'Rule M / SARSA', 'runs': 50, 'scope': 'Full trajectory audit, cohort arithmetic, and descriptive comparison; publication review remains.'}, indent=2) + '\n')
print('Rule M / SARSA audit, R crosscheck, and curve comparison complete', flush=True)
