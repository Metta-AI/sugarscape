from pathlib import Path
import gzip
import hashlib
import json
import math
import sys
import tarfile
import zipfile

root, output = map(Path, sys.argv[1:])
assert not output.exists()
found = json.loads((root / 'raw-readback.json').read_text())
inventory_path = root.parent / 'need-for-greed-retained-audit-reuse-001/inventory.json'
inventory = json.loads(inventory_path.read_text())
by_entry = {row['entry']: row for row in inventory['runs']}
archive_hashes = {row['path']: row['sha256'] for row in found['archives']}
paper = root.parent / 'papers/need-for-greed.zip'
assert hashlib.sha256(paper.read_bytes()).hexdigest() == 'e41c89ed31811b2d100c0a54f9c0110f0572a980b599e2417b2653b934fbe440'
verified = []
with zipfile.ZipFile(paper) as deposited:
    for archive in sorted({row['archive'] for row in found['matches']}):
        assert hashlib.sha256(Path(archive).read_bytes()).hexdigest() == archive_hashes[archive]
        with tarfile.open(archive) as bundle:
            for row in found['matches']:
                if row['archive'] != archive:
                    continue
                expected = by_entry[row['entry']]
                prefix = row['member'].rsplit('/', 1)[0]
                original = bundle.extractfile(prefix + '/original.config').read()
                assert original == deposited.read(row['entry'])
                assert hashlib.sha256(original).hexdigest() == expected['config_sha256']
                manifest = json.load(bundle.extractfile(prefix + '/manifest.json'))
                assert manifest['entry'] == row['entry']
                assert manifest['release'] == 'b9ca671ab7591c7b3606f2d76c33eda344d626d1'
                assert manifest['pythonhashseed'] == '0'
                assert manifest['source_sha256'] == inventory['source_sha256']
                assert manifest['original_config_sha256'] == expected['config_sha256']
                assert set(manifest['changes']) == {'logfile'}
                config_raw = bundle.extractfile(prefix + '/config.json').read()
                assert hashlib.sha256(config_raw).hexdigest() == manifest['config_sha256']
                config = json.loads(config_raw)
                assert config == json.loads(original) | {'logfile': manifest['changes']['logfile']['effective']}
                raw = bundle.extractfile(row['member']).read()
                if row['member'].endswith('.gz'):
                    raw = gzip.decompress(raw)
                assert hashlib.sha256(raw).hexdigest() == row['trajectory_sha256'] == expected['result']['trajectory_sha256']
                records = json.loads(raw)
                assert len(records) == row['observations'] == expected['result']['observations']
                assert records[-1]['population'] == row['final_population'] == expected['result']['final_population']
                assert records[-1]['timestep'] == 5000 or records[-1]['population'] == 0
                for timestep, record in enumerate(records):
                    assert record['timestep'] == timestep
                    assert all(math.isfinite(value) for value in record.values() if isinstance(value, (int, float)))
                verified.append(row)
assert len({row['entry'] for row in verified}) == len(verified) == 64
report = {'native_runs_verified': len(verified), 'observations': sum(row['observations'] for row in verified),
          'models': sorted({row['model'] for row in verified}),
          'candidate_inventory_sha256': hashlib.sha256(inventory_path.read_bytes()).hexdigest(),
          'archive_sha256': {name: archive_hashes[name] for name in sorted({row['archive'] for row in verified})},
          'runs': verified,
          'remaining_baseline_raw_checks': 400 - len(verified),
          'scope': 'Fresh archive/configuration/manifest/raw-trajectory verification of 64 shared Bentham baseline inputs. Original paper configurations are byte-identical. No sweep endpoint substitution, new simulations, full baseline claim, or completed-paper credit.'}
output.write_text(json.dumps(report, indent=2) + '\n')
print('Verified', len(verified), 'native inputs and', report['observations'], 'observations')
