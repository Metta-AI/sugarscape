"""Read pinned remote objects in bounded batches, retaining each verified file."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import gzip
import hashlib
import json
import shutil
import subprocess
import time

root = Path(__file__).resolve().parent
published = root.parent.parent / 'sugarscape-quera/replications/quera_2025/results/perturbed-movement-complete-2026-10-18'
manifest = gzip.decompress((published / 'sha256.txt.gz').read_bytes())
assert hashlib.sha256(manifest).hexdigest() == '5bbef175c58ee5d0230000d89177bc7c5c9bcda5fa4bc94a5539573cb194bd76'
expected = dict(line.split('  ', 1)[::-1] for line in manifest.decode().splitlines())
expected['sha256.txt'] = hashlib.sha256(manifest).hexdigest()
assert len(expected) == 36724
assert all(not Path(name).is_absolute() and '..' not in Path(name).parts for name in expected)
assert shutil.disk_usage(root).free > 8 * 1024**3
native = root / 'native'
native.mkdir(exist_ok=True)
partial = root / f'partial-{time.time_ns()}'
partial.mkdir()
existing = {str(p.relative_to(native)): hashlib.sha256(p.read_bytes()).hexdigest() for p in native.rglob('*') if p.is_file()}
assert all(name in expected and digest == expected[name] for name, digest in existing.items())
missing = sorted(set(expected) - set(existing))
prefix = 'quera-perturbed-movement-ensemble-001/native/'
started = time.monotonic()
total_bytes = sum(p.stat().st_size for p in native.rglob('*') if p.is_file())


def download(item):
    name = item['key'].removeprefix(prefix)
    assert item['key'] == prefix + name and name in expected
    target = native / name
    temp = partial / name
    assert not target.exists()
    temp.parent.mkdir(parents=True, exist_ok=True)
    target.parent.mkdir(parents=True, exist_ok=True)
    config = 'url = ' + json.dumps(item['download']['url']) + '\n'
    process = subprocess.run(['curl', '--fail', '--silent', '--show-error', '--max-time', '90', '--config', '-', '--output', str(temp)], input=config, capture_output=True, text=True, timeout=100)
    assert process.returncode == 0, f"Object download failed: {name}; curl exit {process.returncode}. Partial bytes retained."
    assert temp.stat().st_size == item['size_bytes']
    assert hashlib.sha256(temp.read_bytes()).hexdigest() == expected[name], name
    temp.rename(target)
    return target.stat().st_size


def metadata(names):
    response = json.loads(subprocess.check_output(['/Users/relh/.local/bin/autor', 'api', 'post', '/storage/relh-sugarscape-evidence-20261017/objects/download-batch', '--data', json.dumps({'keys': [prefix + name for name in names]}), '--json'], text=True, timeout=60))
    assert response['failed'] == [] and response['count'] == len(names)
    items = response['downloads']
    assert len(items) == len(names) and {item['key'] for item in items} == {prefix + name for name in names}
    return items


with (root / 'progress.jsonl').open('a') as log:
    for offset in range(0, len(missing), 32):
        assert time.monotonic() - started < 7200
        names = missing[offset:offset + 32]
        with ThreadPoolExecutor(max_workers=4) as signing:
            groups = signing.map(metadata, [names[i:i + 8] for i in range(0, len(names), 8)])
            items = [item for group in groups for item in group]
        assert len(items) == len(names) and {item['key'] for item in items} == {prefix + name for name in names}
        assert total_bytes + sum(item['size_bytes'] for item in items) <= 5 * 1024**3
        with ThreadPoolExecutor(max_workers=32) as workers:
            total_bytes += sum(workers.map(download, items))
        row = {'verified_objects': len(existing) + offset + len(names), 'total_objects': len(expected), 'bytes': total_bytes, 'elapsed_seconds': time.monotonic() - started}
        log.write(json.dumps(row) + '\n')
        log.flush()
        print(json.dumps(row), flush=True)
actual = {str(p.relative_to(native)): hashlib.sha256(p.read_bytes()).hexdigest() for p in native.rglob('*') if p.is_file()}
assert actual == expected
prior = json.loads(gzip.decompress((published / 'audit.json.gz').read_bytes()))
assert len(prior['runs']) == 9180 and all(row['maximum_absolute_state_error'] == 0 for row in prior['runs'])
assert {row['case']['case'] + suffix for row in prior['runs'] for suffix in ['-agents.csv.gz', '-cells.csv.gz', '-orders.csv.gz', '-parameters.csv.gz']} == {name for name in expected if name.endswith('.csv.gz')}
report = {'objects_verified': len(actual), 'trace_objects_verified': 36720, 'prior_replayed_cases': 9180, 'total_object_bytes': total_bytes, 'manifest_sha256': hashlib.sha256(manifest).hexdigest(), 'all_remote_objects_match_replayed_manifest': True, 'scope': 'Full fresh remote readback equals previously replayed manifest; no new simulations or repeat state replay. Failed earlier downloads retain no completion credit.'}
(root / 'audit.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report), flush=True)
