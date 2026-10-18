"""Audit the complete deposited pension experiment grid and compare new and archived samples."""
import argparse
from collections import defaultdict
import csv
import hashlib
import itertools
import json
import math
from pathlib import Path
import statistics
import xml.etree.ElementTree as ET

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('native', type=Path)
parser.add_argument('source', type=Path)
parser.add_argument('output', type=Path)
args = parser.parse_args()
assert not args.output.exists()
# Require the producer's terminal evidence before reading an active CSV.
completion = json.loads((args.native / 'completed.json').read_text())
for name, digest in completion['files_sha256'].items():
    assert hashlib.sha256((args.native / name).read_bytes()).hexdigest() == digest, name
protocol = json.loads((args.native / 'protocol.json').read_text())
assert hashlib.sha256((args.native / 'run.py').read_bytes()).hexdigest() == protocol['runner_sha256']
assert protocol['seed_base'] == 20261018 and protocol['steps'] == 1000
source = args.source / 'Sugarscape Pension Law.nlogo'
assert hashlib.sha256(source.read_bytes()).hexdigest() == protocol['source_sha256'] == '3cd89b39a9bfdd30adb84b6ed6056215097a26bfd9eaa39dc524e8dedb6fc27d'
archived = args.source / 'Sugarscape Pension Law pensionsExperiments-table.csv'
assert hashlib.sha256(archived.read_bytes()).hexdigest() == '627bbaa69cd0c3dffc6a7a093db6b354f45c79510cd0128c124cac1080270690'
folder = args.native / 'full-grid'
assert json.loads((folder / 'exit.json').read_text())['exit_code'] == 0
assert not (folder / 'stderr.log').read_bytes()
text = source.read_text()
original = next(x for x in ET.fromstring(text[text.index('<experiments>'):text.index('</experiments>')+14]) if x.attrib['name'] == 'pensionsExperiments')
actual = ET.parse(folder / 'experiment.xml').getroot()[0]
assert actual.attrib == original.attrib
assert actual.find('setup').text == 'random-seed (20261018 + behaviorspace-run-number) setup'
for tag in ['go','timeLimit']:
    assert ET.tostring(actual.find(tag)) == ET.tostring(original.find(tag))
assert [(x.attrib, [v.attrib for v in x]) for x in actual.findall('enumeratedValueSet')] == [(x.attrib,[v.attrib for v in x]) for x in original.findall('enumeratedValueSet')]
metrics = [x.text for x in original.findall('metric')]
assert [x.text for x in actual.findall('metric')] == metrics + ['20261018 + behaviorspace-run-number','count turtles']
parameters = ['initial-population','retirement-age','pension-taxes','fixed-fee']
expected_grid = set(itertools.product([400.,800.],[100.,65.,67.,70.],[0.,4.7,10.,28.3],[0.,.1,.5,1.]))
fixed = {'minimum-sugar-endowment':'5','maximum-sugar-endowment':'25','visualization':'no-visualization','random-initial-age':'true','resources-occupation':'true','social-services':'false','productivity-decay':'false'}
groups = {}
for label, path in [('archived',archived),('new',folder/'trajectory.csv')]:
    with path.open(newline='') as stream:
        rows=list(csv.reader(stream))
    assert rows[0] == ['BehaviorSpace results (NetLogo 6.1.0)'] and rows[2] == ['pensionsExperiments']
    assert rows[5] == ['0','49','0','49']
    records=[dict(zip(rows[6],row,strict=True)) for row in rows[7:]]
    assert len(records)==1280 and {int(r['[run number]']) for r in records}==set(range(1,1281))
    grouped=defaultdict(list)
    for record in records:
        assert int(record['[step]'])==1000
        assert all(record[k]==v for k,v in fixed.items())
        values=[float(record[k]) for k in metrics]
        assert all(map(math.isfinite,values)) and 0<=values[2]<=1
        assert all(v>=0 and v==int(v) for v in values[3:])
        assert values[5]==values[3]+values[4]
        if label=='new':
            assert int(record['20261018 + behaviorspace-run-number'])==20261018+int(record['[run number]'])
            assert int(record['count turtles'])==int(record['initial-population'])
        grouped[tuple(float(record[k]) for k in parameters)].append(values)
    assert set(grouped)==expected_grid and {len(v) for v in grouped.values()}=={10}
    groups[label]=grouped
comparisons=[]
for condition in sorted(expected_grid):
    for index,metric in enumerate(metrics):
        estimates={}
        for label in ['archived','new']:
            values=[row[index] for row in groups[label][condition]]
            estimates[label]={'mean':statistics.mean(values),'sample_standard_deviation':statistics.stdev(values),'replicate_standard_error':statistics.stdev(values)/math.sqrt(10)}
        comparisons.append({'condition':dict(zip(parameters,condition,strict=True)),'metric':metric,'estimates':estimates,'new_minus_archived_mean':estimates['new']['mean']-estimates['archived']['mean']})
report={'conditions':128,'replicates_per_condition':10,'new_runs':1280,'archived_runs':1280,'comparisons':comparisons,'native_csv_sha256':hashlib.sha256((folder/'trajectory.csv').read_bytes()).hexdigest(),'auditor_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'scope':'Descriptive comparison of new declared seeds and archived outputs. No recovered historical random streams, confidence-based equivalence margin, full paper access, or paper-level verdict.'}
with args.output.open('x') as stream:json.dump(report,stream,indent=2,allow_nan=False)
print(json.dumps({k:v for k,v in report.items() if k!='comparisons'}))
