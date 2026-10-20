"""Reconstruct exported run measurements from all audited timestep CSV records."""
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('phase3', type=Path)
p.add_argument('phase2', type=Path)
p.add_argument('analysis', type=Path)
p.add_argument('output', type=Path)
a = p.parse_args()
with (a.analysis/'run-measurements.csv').open() as stream:
    rows = list(csv.DictReader(stream))
assert len(rows) == 21600
expected = {(r['condition'], int(r['seed']), r['metric']): r['value'] for r in rows}
assert len(expected) == len(rows)
actual = {}
hashes = {}
record_count = 0
for directory, phase, count in [(a.phase3,3,1200),(a.phase2,2,600)]:
    report = json.loads((directory/'reconciliation.json').read_text())
    assert report['complete_grid'] and report['validated_runs']==count
    groups = {}
    for index, segment in enumerate(report['segments']):
        path = directory/f'segment-{index:02d}'/'price-measurements.csv'
        hashes[str(path)] = hashlib.sha256(path.read_bytes()).hexdigest()
        with path.open() as stream:
            for r in csv.DictReader(stream):
                selector = r['selector'] if phase==3 else 'none'
                key = (f"{r['approach']}-{r['threshold']}-{selector}",int(r['numpy_seed']))
                groups.setdefault(key,{})
                step=int(r['step'])
                assert step not in groups[key]
                groups[key][step]=r
                record_count+=1
    assert len(groups)==count
    for (condition,seed), steps in groups.items():
        assert set(steps)==set(range(1,1001))
        actual[condition,seed,'undefined_dispersion_steps']=sum(int(r['trades'])<2 for r in steps.values())
        for window,begin,end in [('early',1,100),('late',901,1000)]:
            selected=[steps[s] for s in range(begin,end+1)]
            actual[condition,seed,window+'_trades']=sum(int(r['trades']) for r in selected)
            for metric,minimum in [('geometric_mean_price',1),('sample_sd_log_price',2)]:
                assert all((r[metric]!='')==(int(r['trades'])>=minimum) for r in selected)
                defined=[float(r[metric]) for r in selected if r[metric]!='']
                actual[condition,seed,window+'_'+metric]=math.fsum(defined)/len(defined) if defined else None
                actual[condition,seed,window+'_'+metric+'_defined_steps']=len(defined)
    for r in report['runs']:
        selector=r['selector'] if phase==3 else 'none'
        condition=f"{r['approach']}-{r['threshold']}-{selector}"
        actual[condition,r['numpy_seed'],'survivors']=r['final_individual_agents']
assert record_count==1800000 and set(actual)==set(expected)
errors=[]
missing=0
for key,value in actual.items():
    if value is None:
        assert expected[key]==''
        missing+=1
    else:
        assert expected[key]!=''
        errors.append(abs(value-float(expected[key])))
assert max(errors)<1e-10
result={'timestep_records':record_count,'run_measurements':len(actual),'undefined_measurements':missing,'maximum_absolute_difference':max(errors),'input_sha256':hashes,'scope':'All 19800 price/count measurements independently reconstructed from audited timestep CSVs;1800 survivor measurements checked against raw-audit summaries. Statistical intervals verified separately in R. Does not establish historical source fidelity.'}
a.output.write_text(json.dumps(result,indent=2)+'\n')
print({k:v for k,v in result.items() if k!='input_sha256'})
