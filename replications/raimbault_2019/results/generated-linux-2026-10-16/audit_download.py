"""Independently compare completed Linux probes with source data and macOS outputs."""
from pathlib import Path
import csv
import gzip
import hashlib
import io
import json
import math
import tarfile

root = Path(__file__).resolve().parent
mac = root.parent / 'raimbault-generated-diversity-001'
archive = root / 'generated-linux-001.tar.gz'
selection = json.loads((mac / 'selection.json').read_text())
criteria = json.loads((mac / 'criteria.json').read_text())
with gzip.open(mac / 'selected.csv.gz', 'rt') as stream:
    reference = list(csv.DictReader(stream))
metrics = ['gini', 'mwgini', 'moran', 'distance', 'entropy', 'slope', 'rsquared', 'moranRessource', 'distanceRessource', 'entropyRessource', 'slopeRessource', 'rsquaredRessource']
comparisons = []
with tarfile.open(archive) as tar:
    def read(name):
        return tar.extractfile('generated-linux-001/' + name).read()
    assert json.loads(read('terminal.json'))['exit_code'] == 0
    for name in ['run.py', 'run.sh', 'criteria.json', 'selection.json', 'selected.csv.gz', 'GeneratedReplay.java', 'expected-runtime.json']:
        assert read(name) == (root / name).read_bytes(), name
    runtime = json.loads(read('expected-runtime.json'))
    runtime['GeneratedReplay.java'] = hashlib.sha256(read('GeneratedReplay.java')).hexdigest()
    all_exact = True
    durations = []
    for start, stop in [(0,2), (2,4), (4,6)]:
        pair = f'run-{start}-{stop}'
        terminal = json.loads(read(pair + '/exit.json'))
        assert terminal['exit_code'] == 0
        durations.append(terminal['seconds'])
        manifest = json.loads(read(pair + '/manifest.json'))
        for name, checksum in runtime.items():
            prefix = '/root/sugarscape/generated-linux-001/' if name == 'GeneratedReplay.java' else '/root/sugarscape/proof-002/'
            assert manifest['source_sha256'][prefix + name] == checksum, name
        raw = read(pair + '/results.csv')
        macraw = (mac / pair / 'results.csv').read_bytes()
        all_exact &= raw == macraw
        linux = list(csv.DictReader(io.StringIO(raw.decode())))
        macrows = list(csv.DictReader(io.StringIO(macraw.decode())))
        assert len(linux) == len(macrows) == stop - start
        for index, (row, macrow) in enumerate(zip(linux, macrows), start):
            expected = reference[index]
            assert int(row['row']) == index and row['seed'] == expected['replication'] and row['id'] == expected['id']
            assert float(row['population']) == float(expected['population']) and float(row['ticks']) == 10000
            for metric in metrics:
                actual = float(row[metric]); historical = float(expected[metric]); macvalue = float(macrow[metric])
                assert all(map(math.isfinite, [actual, historical, macvalue]))
                tolerance = 0 if metric in ['gini', 'mwgini'] else criteria['morphology_absolute_tolerance']
                comparisons.append({'original_row': selection['original_indices'][index], 'metric': metric, 'linux': actual, 'macos': macvalue, 'archive': historical, 'linux_archive_error': abs(actual-historical), 'linux_macos_error': abs(actual-macvalue), 'tolerance': tolerance})
    report = {'rows':6, 'measurements':len(comparisons), 'linux_macos_byte_identical':all_exact, 'linux_archive_exact':sum(x['linux_archive_error']==0 for x in comparisons), 'linux_macos_exact':sum(x['linux_macos_error']==0 for x in comparisons), 'within_declared_tolerances':all(x['linux_archive_error']<=x['tolerance'] and x['linux_macos_error']<=x['tolerance'] for x in comparisons), 'maximum_archive_error':max(x['linux_archive_error'] for x in comparisons), 'maximum_platform_error':max(x['linux_macos_error'] for x in comparisons), 'pair_seconds':durations, 'archive_sha256':hashlib.sha256(archive.read_bytes()).hexdigest(), 'scope':'Repeated validation probes only; no production coverage. Full generated ensemble remains unstarted.'}
(root / 'independent-comparisons.json').write_text(json.dumps(comparisons,indent=2)+'\n')
(root / 'independent-validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))
assert report['within_declared_tolerances']
