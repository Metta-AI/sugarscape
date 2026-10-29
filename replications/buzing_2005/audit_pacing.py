"""Compare complete paced/unpaced native grids, including the exact source change."""
import argparse
import hashlib
import json
from pathlib import Path
import re

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('paced', type=Path)
parser.add_argument('unpaced', type=Path)
parser.add_argument('output', type=Path)
args = parser.parse_args()
expected = [f'paper-com{model}-ct{threshold}-seed{seed}' for model in range(3) for threshold in range(5) for seed in range(10)]
for root in (args.paced, args.unpaced):
    assert json.loads((root / 'exit.json').read_text()) == {'exit_code': 0, 'completed_runs': 150}
    ledger = [json.loads(line) for line in (root / 'completed.jsonl').read_text().splitlines()]
    assert [r['name'] for r in ledger] == expected and all(r['exit_code'] == 0 for r in ledger)
rows = []
for name in expected:
    left, right = args.paced / name, args.unpaced / name
    a, b = [json.loads((p / 'manifest.json').read_text()) for p in (left, right)]
    for key in ('variant', 'threshold', 'seed', 'cycles', 'archive_sha256', 'adapter_sha256', 'java_version', 'source_count'):
        assert a[key] == b[key], (name, key)
    source_maps = []
    for manifest in (a, b):
        sources = {}
        for filename, checksum in manifest['source_sha256'].items():
            source = Path(filename)
            raw = source.read_bytes()
            assert hashlib.sha256(raw).hexdigest() == checksum
            package = re.search(rb'(?m)^\s*package\s+([\w.]+)\s*;', raw)
            assert package is not None
            relative = package[1].decode() + '.' + source.name
            assert relative not in sources
            sources[relative] = raw
        source_maps.append(sources)
    assert source_maps[0].keys() == source_maps[1].keys()
    changed = []
    for filename, raw in source_maps[0].items():
        if raw != source_maps[1][filename]:
            assert filename == 'nl.vu.cs.sugarland.model.Scape.java'
            assert raw.count(b'Thread.sleep(SLEEP_TIME);') == 1
            assert raw.replace(b'Thread.sleep(SLEEP_TIME);', b'// Headless execution: omit wall-clock pacing only.') == source_maps[1][filename]
            changed.append(filename)
    assert changed == ['nl.vu.cs.sugarland.model.Scape.java']
    assert a['configuration_sha256'] == b['configuration_sha256']
    for filename, checksum in a['configuration_sha256'].items():
        assert (left / filename).read_bytes() == (right / filename).read_bytes()
        assert hashlib.sha256((left / filename).read_bytes()).hexdigest() == checksum
    assert a['output_sha256'] == b['output_sha256'] and len(a['output_sha256']) == 10
    for filename, checksum in a['output_sha256'].items():
        raw = (left / filename).read_bytes()
        assert raw == (right / filename).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == checksum
    counts = [[line for line in (p / 'run.log').read_text().splitlines() if line.startswith('harvest-counts,')] for p in (left, right)]
    assert counts[0] == counts[1] and len(counts[0]) == 2000
    rows.append({'name': name, 'matching_native_files': 10, 'matching_harvest_rows': 2000,
                 'only_source_change': changed, 'native_output_sha256': a['output_sha256'],
                 'paced_manifest_sha256': hashlib.sha256((left / 'manifest.json').read_bytes()).hexdigest(),
                 'unpaced_manifest_sha256': hashlib.sha256((right / 'manifest.json').read_bytes()).hexdigest()})
args.output.mkdir(parents=True, exist_ok=False)
report = {'matched_runs': len(rows), 'matching_native_files': 1500, 'matching_harvest_rows': 300000,
          'paced': str(args.paced.resolve()), 'unpaced': str(args.unpaced.resolve()), 'pairs': rows,
          'scope': 'Exact pacing equivalence over the complete reconstruction grid. Paired runs do not add independent seeds or establish historical model fidelity.'}
(args.output / 'audit.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps({k:v for k,v in report.items() if k != 'pairs'}))
