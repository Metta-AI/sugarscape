from pathlib import Path
import hashlib
import json
import subprocess
import tarfile

root = Path(__file__).resolve().parent
campaign = root.parent / 'quera-full-calibration-001'
figures = root.parent / 'quera-calibration-figures-reviewed-001'
preflight = json.loads((root / 'storage-preflight.json').read_bytes())
assert preflight['objects'] == [] and not preflight['truncated']
assert json.loads((campaign / 'predictive-terminal.json').read_bytes())['native_trajectories'] == 4000
sources = {f'predictive/{p.name}': p for p in sorted((campaign / 'predictive').iterdir())}
for name in ['predictive-summary.json', 'predictive-r.json', 'predictive-terminal.json', 'predictive-native-exit.json', 'predict.jl', 'protocol.json', 'verify_predictive.R', 'predictive-audit.log']:
    sources['campaign/' + name] = campaign / name
for name in ['analyze_predictive.py', 'amendment.json', 'audit.log', 'r.log']:
    sources['amended-audit/' + name] = root / name
for name in ['predictive.pdf', 'posterior-pairs.pdf', 'training.pdf', 'render.json']:
    sources['figures/' + name] = figures / 'figures' / name
for name in ['render.R', 'render-amendment.json']:
    sources['figures/' + name] = figures / name
assert all(p.is_file() and not p.is_symlink() for p in sources.values())
expected = {n: {'bytes': p.stat().st_size, 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()} for n, p in sources.items()}
archive = root / 'predictive-evidence.tar.gz'
with tarfile.open(archive, 'x:gz') as bundle:
    for name, path in sources.items():
        bundle.add(path, arcname=name, recursive=False)
assert archive.stat().st_size < 128 * 1024**2
key = 'relh-sugarscape-evidence-20261017/quera-full-predictive-20261020-001/predictive-evidence.tar.gz'
readback = root / 'storage-predictive-evidence.tar.gz'
assert not readback.exists()
for direction, paths in [('upload', [str(archive), key]), ('download', [key, str(readback)])]:
    with (root / f'storage-{direction}.json').open('x') as log:
        subprocess.run(['autor', 'storage', 'cp', *paths, '--json'], stdout=log, check=True, timeout=600)
assert readback.stat().st_size == archive.stat().st_size
assert hashlib.sha256(readback.read_bytes()).hexdigest() == hashlib.sha256(archive.read_bytes()).hexdigest()
with tarfile.open(readback) as bundle:
    members = bundle.getmembers()
    assert len({m.name for m in members}) == len(members) and all(m.isfile() for m in members)
    actual = {m.name: {'bytes': m.size, 'sha256': hashlib.sha256(bundle.extractfile(m).read()).hexdigest()} for m in members}
assert actual == expected
(root / 'storage-readback.json').write_text(json.dumps({'object': key, 'archive_bytes': archive.stat().st_size, 'archive_sha256': hashlib.sha256(archive.read_bytes()).hexdigest(), 'all_fresh_remote_members_match': True, 'members': actual, 'native_trajectories': 4000}, indent=2) + '\n')
print('Full predictive evidence freshly read back and verified', flush=True)
