import csv
import hashlib
import json
import math
import shutil
import subprocess
import time
from pathlib import Path

root = Path(__file__).resolve().parent
plan = json.loads((root / 'plan.json').read_text())
commands = json.loads((root / 'commands.json').read_text())
for name, expected in json.loads((root / 'input-sha256.json').read_text()).items():
    assert hashlib.sha256((root / name).read_bytes()).hexdigest() == expected, name
started = time.monotonic()
results = []
for entry in commands:
    directory = Path(entry['directory'])
    for kind in ('custom', 'native'):
        remaining = plan['overall_timeout_seconds'] - (time.monotonic() - started)
        assert remaining > 0
        assert shutil.disk_usage(root).free > plan['minimum_free_bytes']
        start = time.monotonic()
        with (directory / f'{kind}-terminal.log').open('x') as log:
            process = subprocess.run(entry[kind], cwd=root, stdout=log, stderr=subprocess.STDOUT,
                                     timeout=min(remaining, plan['per_run_timeout_seconds']))
        receipt = {'exit_code': process.returncode, 'elapsed_seconds': time.monotonic() - start}
        (directory / f'{kind}-terminal.json').write_text(json.dumps(receipt, indent=2) + '\n')
        assert process.returncode == 0, (entry['pairing'], kind)
        assert sum(p.stat().st_size for p in root.rglob('*') if p.is_file()) < plan['maximum_bytes']
    with (directory / 'trajectory.csv').open() as f:
        recorded = list(csv.DictReader(f))
    lines = (directory / 'native-table.csv').read_text().splitlines()
    index = next(i for i, row in enumerate(csv.reader(lines)) if row and row[0] == '[run number]')
    reference = list(csv.DictReader(lines[index:]))
    assert len(recorded) == len(reference) == plan['steps'] + 1
    fields = list(recorded[0])[1:]
    assert fields == next(csv.reader([lines[index]]))[10:]
    for tick, (actual, expected) in enumerate(zip(recorded, reference)):
        assert float(actual['tick']) == float(expected['[step]']) == tick
        for field in fields:
            a, b = float(actual[field]), float(expected[field])
            assert math.isfinite(a) and math.isfinite(b)
            assert a == b, (entry['pairing'], tick, field, a, b)
    result = {'pairing': entry['pairing'], 'observations': len(recorded),
              'compared_fields': len(recorded) * len(fields), 'differences': [],
              'trajectory_sha256': hashlib.sha256((directory / 'trajectory.csv').read_bytes()).hexdigest(),
              'native_table_sha256': hashlib.sha256((directory / 'native-table.csv').read_bytes()).hexdigest()}
    (directory / 'comparison.json').write_text(json.dumps(result, indent=2) + '\n')
    results.append(result)
    with (root / 'completed-pairings.jsonl').open('a') as f:
        f.write(json.dumps(result) + '\n')
    print(json.dumps(result), flush=True)
(root / 'terminal.json').write_text(json.dumps({'exit_code': 0, 'elapsed_seconds': time.monotonic() - started,
                                               'completed_pairings': len(results)}, indent=2) + '\n')
