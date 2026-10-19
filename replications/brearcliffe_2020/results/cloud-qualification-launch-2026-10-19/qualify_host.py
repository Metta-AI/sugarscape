import csv
import hashlib
import json
import math
import platform
import subprocess
import time
from pathlib import Path

root = Path(__file__).resolve().parent
plan = json.loads((root / 'plan.json').read_text())
for name, digest in json.loads((root / 'payload-sha256.json').read_text()).items():
    assert hashlib.sha256((root / name).read_bytes()).hexdigest() == digest, name
cases = json.loads((root / 'cases.json').read_text())
for case in cases:
    comparison = json.loads((root / 'gates' / f"{case['name']}.json").read_text())
    assert comparison['compared_fields'] == 320016 and comparison['differences'] == []
    assert comparison['observations'] == 20001
    assert comparison['trajectory_sha256'] == case['sha256']
    assert hashlib.sha256((root / case['reference']).read_bytes()).hexdigest() == case['sha256']
output = root / 'results'
output.mkdir()
version = subprocess.run(['java', '-version'], capture_output=True, text=True, check=True)
(output / 'runtime.json').write_text(json.dumps({'platform': platform.platform(), 'python': platform.python_version(),
                                                'java': version.stdout + version.stderr}, indent=2) + '\n')
started = time.monotonic()
results = []
for case in cases:
    directory = output / case['name']
    directory.mkdir()
    command = ['java', '-Xmx1g', '-Djava.awt.headless=true', '-cp', str(root / 'assets') + ':' + str(root / 'app/*'),
               'Replay', str(root / 'assets/model.nlogo'), case['group_A'], case['group_B'], '20000',
               str(directory / 'trajectory.csv')]
    (directory / 'command.json').write_text(json.dumps(command, indent=2) + '\n')
    remaining = plan['overall_qualification_seconds'] - (time.monotonic() - started)
    assert remaining > 0
    before = time.monotonic()
    with (directory / 'terminal.log').open('x') as log:
        process = subprocess.run(command, cwd=root / 'assets', stdout=log, stderr=subprocess.STDOUT,
                                 timeout=min(remaining, plan['timeout_per_case_seconds']))
    receipt = {'exit_code': process.returncode, 'elapsed_seconds': time.monotonic() - before}
    (directory / 'terminal.json').write_text(json.dumps(receipt, indent=2) + '\n')
    assert process.returncode == 0
    assert sum(p.stat().st_size for p in output.rglob('*') if p.is_file()) < plan['maximum_result_bytes']
    with (directory / 'trajectory.csv').open() as file:
        actual = list(csv.DictReader(file))
    with (root / case['reference']).open() as file:
        expected = list(csv.DictReader(file))
    assert len(actual) == len(expected) == 20001
    assert list(actual[0]) == list(expected[0])
    for tick, (a, b) in enumerate(zip(actual, expected)):
        assert float(a['tick']) == float(b['tick']) == tick
        for field in list(a)[1:]:
            left, right = float(a[field]), float(b[field])
            assert math.isfinite(left) and math.isfinite(right)
            assert left == right, (case['name'], tick, field, left, right)
    result = {'case': case['name'], 'observations': len(actual), 'compared_fields': len(actual) * 16,
              'differences': [], 'elapsed_seconds': receipt['elapsed_seconds'],
              'trajectory_sha256': hashlib.sha256((directory / 'trajectory.csv').read_bytes()).hexdigest()}
    (directory / 'comparison.json').write_text(json.dumps(result, indent=2) + '\n')
    results.append(result)
    print(json.dumps(result), flush=True)
(output / 'summary.json').write_text(json.dumps({'exit_code': 0, 'cases': results,
                                                'elapsed_seconds': time.monotonic() - started}, indent=2) + '\n')
