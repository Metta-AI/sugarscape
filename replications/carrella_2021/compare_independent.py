"""Describe native/independent differences after auditing every completed trajectory."""
import argparse
import csv
import hashlib
import io
import json
import math
from pathlib import Path
import statistics
import subprocess
import sys

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('parameters', type=Path)
parser.add_argument('reference', type=Path)
parser.add_argument('run', type=Path)
parser.add_argument('mode', choices=['prefix', 'complete'])
parser.add_argument('output', type=Path)
args = parser.parse_args()
assert not args.output.exists()
manifest_bytes = (args.run / 'manifest.json').read_bytes()
manifest = json.loads(manifest_bytes)
reference_bytes = args.reference.read_bytes()
assert hashlib.sha256(reference_bytes).hexdigest() == manifest['reference_sha256']
reference = list(csv.DictReader(io.StringIO(reference_bytes.decode())))
assert len(reference) == 5000
subprocess.run([sys.executable, str(Path(__file__).with_name('audit_independent.py')),
                str(args.parameters), str(args.run), args.mode, str(args.output / 'audit')], check=True)
audit = json.loads((args.output / 'audit/analysis.json').read_text())
start, stop = audit['interval']
summary_bytes = (args.output / 'audit/summary-snapshot.csv').read_bytes()
assert hashlib.sha256(summary_bytes).hexdigest() == audit['summary_sha256']
independent = list(csv.DictReader(io.StringIO(summary_bytes.decode())))[:stop - start]
assert len(independent) == stop - start and len(independent) > 1
assert all(row.keys() == reference[0].keys() for row in independent)
comparisons = []
for name in reference[0]:
    native = [float(row[name]) for row in reference[start:stop]]
    measured = [float(row[name]) for row in independent]
    assert all(math.isfinite(value) for value in native + measured)
    differences = [b - a for a, b in zip(native, measured)]
    native_sd = statistics.pstdev(native)
    comparisons.append({'statistic': name, 'native_mean': statistics.fmean(native),
                        'independent_mean': statistics.fmean(measured),
                        'mean_difference': statistics.fmean(differences),
                        'root_mean_squared_difference': math.sqrt(statistics.fmean(v * v for v in differences)),
                        'native_standard_deviation': native_sd,
                        'absolute_mean_difference_over_native_sd': abs(statistics.fmean(differences)) / native_sd if native_sd else None})
assert len(comparisons) == 150
native_extinct = [i for i in range(start, stop) if float(reference[i]['last_count turtles']) == 0]
report = {'interval': [start, stop], 'complete_original_ensemble': audit['complete_original_ensemble'],
          'native_extinct_inputs': native_extinct, 'independent_extinct_inputs': audit['extinct_inputs'],
          'comparisons': comparisons, 'reference_sha256': hashlib.sha256(reference_bytes).hexdigest(),
          'summary_snapshot_sha256': hashlib.sha256(summary_bytes).hexdigest(),
          'manifest_sha256': hashlib.sha256(manifest_bytes).hexdigest(),
          'analyzer_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
          'scope': 'Descriptive paired-input diagnostic, with different random generators. No trajectory equivalence, significance, equivalence margin, or paper replication verdict. Prefixes are not the complete parameter ensemble.'}
(args.output / 'summary-snapshot.csv').write_bytes(summary_bytes)
(args.output / 'comparison.json').write_text(json.dumps(report, indent=2, allow_nan=False) + '\n')
print(json.dumps({k: report[k] for k in ['interval', 'native_extinct_inputs', 'independent_extinct_inputs']}))
