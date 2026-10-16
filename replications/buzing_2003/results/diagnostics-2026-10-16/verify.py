"""Revalidate retained diagnostic data; source paths require the original preparation."""
import hashlib
import json
import math
from pathlib import Path
import sys
import tarfile

root = Path(sys.argv[1])
report = json.loads((root / 'comparison.json').read_text())
with tarfile.open(root / 'native-evidence.tar.gz') as archive:
    for name, checksum in report['archive_members_sha256'].items():
        assert hashlib.sha256(archive.extractfile(name).read()).hexdigest() == checksum
    for row in report['runs']:
        name = row['name']
        audit = json.loads(archive.extractfile(name + '/audit.json').read())
        provenance = json.loads(archive.extractfile(name + '/provenance.json').read())
        assert json.loads(archive.extractfile(name + '/exit.json').read()) == {'exit_code': 0}
        for key in ('reproduction',):
            assert row[key] == provenance[key] == audit[key]
        configuration = archive.extractfile(name + '/config/Experiment/experiment.cfg').read().decode()
        subcycles = [int(s.split('=', 1)[1]) for s in configuration.splitlines() if s.strip().startswith('nrOfSubcycles')][0]
        assert row['subcycles'] == subcycles
        assert provenance['seed'] == 0 and provenance['cycles'] == 500
        for filename, checksum in provenance['configuration_sha256'].items():
            assert hashlib.sha256(archive.extractfile(name + '/' + filename).read()).hexdigest() == checksum
        series = {}
        for filename, checksum in audit['output_sha256'].items():
            raw = archive.extractfile(name + '/data/' + filename).read()
            assert hashlib.sha256(raw).hexdigest() == checksum
            if filename.endswith('.avg'):
                values = [line.split() for line in raw.decode().splitlines()]
                assert [int(r[0]) for r in values] == list(range(500))
                assert all(len(r) == 2 and math.isfinite(float(r[1])) for r in values)
                series[filename] = [float(r[1]) for r in values]
        assert len(series) == 7
        population = series['experiment_0_.numberOfAgents.avg']
        assert all(v.is_integer() and v >= 0 for v in population)
        extinction = population.index(0)
        assert all(v == 0 for v in population[extinction:])
        assert row['final_population'] == population[-1] == 0
        log = archive.extractfile(name + '/run.log').read().decode()
        assert 'iterations=500,initial=400,final=0' in log
        births = [list(map(float, s.split(',')[1:])) for s in log.splitlines() if s.startswith('birth2003,')]
        fertility = [list(map(int, s.split(',')[1:])) for s in log.splitlines() if s.startswith('birth-fertility,')]
        assert len(births) == len(fertility) == row['births'] == audit['births']
        assert all(len(r) == 3 and 0 <= r[0] < 500 for r in births)
        assert all(len(r) == 7 for r in fertility)
        assert [r[0] for r in births] == [r[0] for r in fertility]
        invalid_fertility = sum(not (r[2] <= r[1] <= r[3] and r[5] <= r[4] <= r[6]) for r in fertility)
        invalid_sugar = sum(r[1] <= 5 or r[2] <= 5 for r in births)
        assert invalid_fertility == row['invalid_fertility_births'] == audit['invalid_fertility_births']
        assert invalid_sugar == row['not_above_sugar_threshold_births'] == audit['not_above_sugar_threshold_births']
        if row['reproduction'] == 'specified':
            assert invalid_fertility == invalid_sugar == 0
    for pair in report['byte_equal_pairs']:
        for filename in pair['files']:
            assert archive.extractfile(pair['left'] + '/data/' + filename).read() == archive.extractfile(pair['right'] + '/data/' + filename).read()
print('Validated nine completed runs, 31,500 scalar observations, and two ten-file parity comparisons.')
