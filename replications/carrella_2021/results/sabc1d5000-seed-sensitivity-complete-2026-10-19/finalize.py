from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import sys
import tarfile
import time

root = Path(__file__).resolve().parent
ensemble = root.parent / 'carrella-sabc1d5000-seed-sensitivity-001'
analyzer = Path('/Users/relh/Code/workspace/sugarscape-carrella/replications/carrella_2021/summarize_estimator_seeds.py')
deadline = time.monotonic() + 1200
while True:
    process = subprocess.run(['ps', '-p', '10366', '-o', 'command='], capture_output=True, text=True)
    if process.returncode != 0:
        assert (ensemble / 'terminal.json').is_file(), 'Producer ended without a complete terminal receipt'
        break
    assert str(ensemble / 'run.py') in process.stdout
    assert time.monotonic() < deadline, 'Finalization wait expired; producer remains untouched'
    time.sleep(20)
terminal = json.loads((ensemble / 'terminal.json').read_text())
assert terminal == {'completed_seeds': list(range(1, 11)), 'exit_code': 0}
with (root / 'analysis-original.log').open('x') as stream:
    subprocess.run([sys.executable, str(analyzer), str(ensemble), str(root / 'analysis-original')], stdout=stream, stderr=subprocess.STDOUT, check=True, timeout=120)
files = sorted(p for p in ensemble.rglob('*') if p.is_file())
assert not any(p.is_symlink() for p in ensemble.rglob('*'))
source_bytes = sum(p.stat().st_size for p in files)
assert source_bytes < 400 * 1024**2
assert shutil.disk_usage(root).free > source_bytes + 350 * 1024**2
pins = {str(p.relative_to(ensemble)): {'bytes': p.stat().st_size, 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()} for p in files}
archive = root / 'native-evidence.tar.gz'
with tarfile.open(archive, 'x:gz') as bundle:
    for p in files:
        bundle.add(p, arcname=str(p.relative_to(ensemble)), recursive=False)
readback = root / 'readback'; readback.mkdir()
seen = set()
retained_csv_bytes = 0
with tarfile.open(archive, 'r|gz') as bundle:
    for member in bundle:
        assert member.isfile() and member.name in pins and member.name not in seen
        data = bundle.extractfile(member).read()
        pin = pins[member.name]
        assert len(data) == pin['bytes'] and hashlib.sha256(data).hexdigest() == pin['sha256']
        assert data == (ensemble / member.name).read_bytes()
        seen.add(member.name)
        if member.name.endswith(('.csv', '.json')):
            target = readback / member.name
            assert not Path(member.name).is_absolute() and '..' not in Path(member.name).parts
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data); retained_csv_bytes += len(data)
assert seen == pins.keys()
with (root / 'analysis-readback.log').open('x') as stream:
    subprocess.run([sys.executable, str(analyzer), str(readback), str(root / 'analysis-readback')], stdout=stream, stderr=subprocess.STDOUT, check=True, timeout=120)
for name in ('summary.json', 'scores.csv', 'source-hashes.json', 'arithmetic.json'):
    assert (root / 'analysis-original' / name).read_bytes() == (root / 'analysis-readback' / name).read_bytes()
report = {'archive_bytes': archive.stat().st_size, 'archive_sha256': hashlib.sha256(archive.read_bytes()).hexdigest(), 'source_bytes': source_bytes, 'archive_members_verified': len(seen), 'source_hashes': pins, 'readback_csv_json_bytes': retained_csv_bytes, 'analysis_repeated_byte_identically_from_archive_csv_json': True, 'fold_rds_archive_bytes_match_previously_R_audited_sources': True, 'analyzer_sha256': hashlib.sha256(analyzer.read_bytes()).hexdigest(), 'scope': 'All archive members freshly byte-verified. CSV/JSON analysis repeated from archive readback; RDS input/prediction audits were performed by the original per-seed workflow, not re-executed from archive.'}
(root / 'archive-validation.json').write_text(json.dumps(report, indent=2) + '\n')
(root / 'terminal.json').write_text(json.dumps({'exit_code': 0, 'seeds': 10, 'predictions': 250000, 'input_cells': 37750000}, indent=2) + '\n')
print('Full ten-seed analysis and archive readback verified', flush=True)
