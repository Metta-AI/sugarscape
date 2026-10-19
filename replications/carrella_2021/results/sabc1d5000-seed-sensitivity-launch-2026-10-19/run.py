import csv
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import time

root = Path(__file__).resolve().parent
source = Path('/Users/relh/Code/workspace/sugarscape-nofreelunch-reference')
primary = Path('/Users/relh/Code/workspace/sugarscape-carrella/replications/carrella_2021/results/sabc1d-5000-2026-10-15')
protocol = json.loads((root / 'protocol.json').read_text())
assert subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=source, text=True).strip() == protocol['source_revision']
assert subprocess.check_output(['git', 'status', '--porcelain'], cwd=source, text=True) == ''
env = dict(os.environ, R_LIBS_USER='/Users/relh/Code/workspace/sugarscape-replication-tools/R-library')
primary_packages = {r['Package']: r['Version'] for r in csv.DictReader((primary / 'packages.csv').open())}
for seed in protocol['seeds']:
    assert shutil.disk_usage(root).free > protocol['minimum_free_bytes_before_seed']
    assert sum(p.stat().st_size for p in root.rglob('*') if p.is_file()) < protocol['max_retained_bytes']
    for name, digest in protocol['hashes'].items():
        assert hashlib.sha256(Path(name).read_bytes()).hexdigest() == digest
    run = root / f'seed-{seed:02d}'
    assert not run.exists()
    command = ['/opt/homebrew/bin/gtimeout', '--signal=TERM', '--kill-after=30', '600',
               '/opt/homebrew/bin/Rscript', '--vanilla', str(root / 'run_estimator.R'),
               str(source), 'sabc_1d', '5000', str(seed), str(run)]
    started = time.monotonic()
    with (root / f'seed-{seed:02d}.log').open('x') as log:
        process = subprocess.run(command, env=env, stdout=log, stderr=subprocess.STDOUT)
    (root / f'seed-{seed:02d}-exit.json').write_text(json.dumps({'command': command, 'exit_code': process.returncode,
        'elapsed_seconds': time.monotonic() - started}, indent=2) + '\n')
    assert process.returncode == 0
    current_packages = {r['Package']: r['Version'] for r in csv.DictReader((run / 'packages.csv').open())}
    assert all(current_packages[k] == primary_packages[k] for k in ['abc', 'abctools', 'R.utils', 'dplyr', 'purrr', 'tidyr', 'readr'])
    for script, arguments in [('audit_inputs.R', [str(primary), str(run), str(root / f'seed-{seed:02d}-input-audit.json')]),
                              ('analyze_estimator.R', [str(run), str(root / f'seed-{seed:02d}-prediction-audit')])]:
        subprocess.run(['/opt/homebrew/bin/gtimeout', '--kill-after=10', '120', '/opt/homebrew/bin/Rscript',
                        '--vanilla', str(root / script), *arguments], env=env, check=True)
    assert json.loads((root / f'seed-{seed:02d}-input-audit.json').read_text())['exact_input_cells'] == 3775000
    print(json.dumps({'audited_seed': seed}), flush=True)
(root / 'terminal.json').write_text(json.dumps({'completed_seeds': protocol['seeds'], 'exit_code': 0}) + '\n')
