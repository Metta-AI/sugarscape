from pathlib import Path
import os, subprocess, sys, json
root=Path(__file__).resolve().parent
repo=Path('/Users/relh/Code/workspace/sugarscape-brearcliffe/replications/brearcliffe_2020')
prepared=root.parent/'brearcliffe-ensemble-preparation-001'
with (root / 'readback-restored.log').open('w') as stream:
    subprocess.run([sys.executable, str(root / 'readback_restored.py')], stdout=stream, stderr=subprocess.STDOUT, timeout=300, check=True)
env = dict(os.environ, R_LIBS_USER='/Users/relh/Code/workspace/sugarscape-replication-tools/R-library')
with (root / 'r-validation.log').open('w') as stream:
    subprocess.run(['/opt/homebrew/bin/Rscript', '--vanilla', str(repo / 'verify_cohort.R'), str(prepared), str(root / 'union-audit-restored/audit.json'), str(root / 'cohort'), str(root / 'r-validation.json')], env=env, stdout=stream, stderr=subprocess.STDOUT, timeout=300, check=True)
with (root / 'comparison.log').open('w') as stream:
    subprocess.run([sys.executable, str(repo / 'compare_curves.py'), str(root / 'cohort'), str(repo / 'results/horizontal-calibration-correction-2026-10-19/metric-curves.json.gz'), str(root / 'comparison')], stdout=stream, stderr=subprocess.STDOUT, timeout=120, check=True)
(root / 'analysis-terminal.json').write_text(json.dumps({'exit_code': 0, 'cohort': 'EC / SARSA', 'runs': 50, 'scope': 'Full trajectory audit, cohort arithmetic, and descriptive comparison; publication review remains.'}, indent=2) + '\n')
print('EC / SARSA audit, R crosscheck, and curve comparison complete', flush=True)
