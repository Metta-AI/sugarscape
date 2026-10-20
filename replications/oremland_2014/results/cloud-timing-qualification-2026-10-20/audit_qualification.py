"""Replay cross-host native recorder parity against pinned local references."""
from pathlib import Path
import hashlib
import json
import math
import sys

root = Path(sys.argv[1])
output = root / 'readback/qualification'
payload = root / 'payload'
complete = json.loads((output / 'complete.json').read_bytes())
assert complete['mode'] == 'qualification' and complete['exit_code'] == 0
assert complete['native_runs'] == 48
assert complete['payload_manifest_sha256'] == hashlib.sha256((payload / 'payload-sha256.json').read_bytes()).hexdigest()
assert (output / 'protocol.json').read_bytes() == (payload / 'protocol.json').read_bytes()
plan = json.loads((output / 'protocol.json').read_bytes())
excluded = {'elapsed_seconds', 'setup_seconds', 'simulation_seconds', 'process_cpu_seconds'}
count = 0
for width in plan['width_order']:
    work = output / f'width-{width}'
    reference = payload / 'reference' / str(width)
    assert json.loads((work / 'terminal.json').read_bytes())['exit_code'] == 0
    assert (work / 'requests.jsonl').read_bytes() == (reference / 'requests.jsonl').read_bytes()
    actual = [json.loads(line) for line in (work / 'results.jsonl').read_text().splitlines()]
    expected = [json.loads(line) for line in (reference / 'timed.jsonl').read_text().splitlines()]
    assert len(actual) == len(expected) == 8
    for a, e in zip(actual, expected, strict=True):
        assert {k: v for k, v in a.items() if k not in excluded} == {k: v for k, v in e.items() if k not in excluded}
        assert all(math.isfinite(a[k]) and a[k] >= 0 for k in excluded)
        assert a['setup_seconds'] > 0 and a['simulation_seconds'] > 0
        assert a['elapsed_seconds'] >= a['setup_seconds'] + a['simulation_seconds']
    count += len(actual)
assert count == 48
print(json.dumps({'native_inputs': count, 'all_non_timing_fields_exact': True, 'scope': 'Qualification only; no benchmark result.'}))
