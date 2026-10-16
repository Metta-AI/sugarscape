import hashlib
import json
from pathlib import Path
import os
import subprocess

root = Path(__file__).resolve().parent
engine = root.parent.parent / 'sugarscape-dtl-replacing-reference'
original = root.parent / 'replacing-disease-matched-runtime-001'
python = root.parent.parent / 'sugarscape-replication-tools/automation-venv/bin/python'
source_hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(engine.glob('*.py'))}
assert source_hashes == json.loads((original / 'manifest.json').read_text())['source_sha256']['archive']
reports = []
for seed in [12345, 12881, 22744]:
    output = root / str(seed)
    output.mkdir()
    baseline = original / f'archive-{seed}'
    config = json.loads((baseline / 'config.json').read_text())
    config['headlessMode'] = False
    config['logfile'] = str(output / 'trajectory.json')
    (output / 'config.json').write_text(json.dumps(config, indent=2) + '\n')
    command = [str(python), str(root / 'gui_driver.py'), str(engine), str(output / 'config.json')]
    with (output / 'stdout.log').open('w') as stdout, (output / 'stderr.log').open('w') as stderr:
        result = subprocess.run(command, cwd=output, env={**os.environ, 'PYTHONHASHSEED': '0', 'PYTHONDONTWRITEBYTECODE':'1', 'TCL_LIBRARY':'/Users/relh/.local/share/uv/python/cpython-3.12.4-macos-aarch64-none/lib/tcl8.6', 'TK_LIBRARY':'/Users/relh/.local/share/uv/python/cpython-3.12.4-macos-aarch64-none/lib/tk8.6'}, stdout=stdout, stderr=stderr, timeout=600)
    (output / 'exit.json').write_text(json.dumps({'exit_code':result.returncode, 'command':command})+'\n')
    assert result.returncode == 0
    actual = (output / 'trajectory.json').read_bytes()
    expected = (baseline / 'trajectory.json').read_bytes()
    assert actual == expected
    rows = json.loads(actual)
    assert len(rows) == 501
    reports.append({'seed':seed, 'native_trajectory_byte_identical':True, 'observations':len(rows), 'sha256':hashlib.sha256(actual).hexdigest(), 'minimum_population':min(r['population'] for r in rows)})
    print(json.dumps(reports[-1]),flush=True)
(root / 'audit.json').write_text(json.dumps({'source_sha256':source_hashes, 'runs':reports, 'scope':'Real Tk GUI disease-coloring/play versus original matched-runtime headless runs; no source rule changes. Does not identify paper revision.'},indent=2)+'\n')
