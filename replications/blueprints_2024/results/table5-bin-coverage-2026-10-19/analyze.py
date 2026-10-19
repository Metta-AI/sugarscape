from pathlib import Path
from collections import Counter
from decimal import Decimal
import json,csv,hashlib,zipfile
r=Path(__file__).resolve().parent
repo=Path('/Users/relh/Code/workspace/sugarscape-blueprints')
source=repo/'replications/blueprints_2024/results/heterogeneous50-complete-2026-10-19/population/per-run.csv'
rows=list(csv.DictReader(source.open()));assert len(rows)==len({x['entry'] for x in rows})==500
population=[int(x['final_population']) for x in rows]
counts={'extinct':sum(p==0 for p in population),'worse_positive':sum(0<p<250 for p in population),'equal_initial':sum(p==250 for p in population),'better':sum(p>250 for p in population)}; assert sum(counts.values())==500
archive=r.parent/'blueprints-selfishness037-batch-001/original-archives/blueprints-heterogeneous.zip'; assert hashlib.sha256(archive.read_bytes()).hexdigest()=='c37aa109e59ca8b96cd295b7f022d6bf56f413aabbf246ca432ff5d4360de91a'
entries={}
with zipfile.ZipFile(archive) as z:
 for name in z.namelist():
  config=json.loads(z.read(name)); condition=config['agentDecisionModels'].count('benthamHalfLookaheadBinary')
  if 46<=condition<=50:
   assert config['startingAgents']==250 and config['timesteps']==5000
   entries[name]={'condition':condition,'seed':config['seed']}
assert Counter(x['condition'] for x in entries.values())=={c:500 for c in range(46,51)}
inventory=repo/'replications/blueprints_2024/results/heterogeneous50-complete-2026-10-19/inventory/inventory.json'; inv=json.loads(inventory.read_text()); completed={x['entry'] for x in inv['excluded_controls'] if x['experiment']=='heterogeneous'}
coverage={c:sum(name in completed for name,v in entries.items() if v['condition']==c) for c in range(46,51)}
target={'paper_sha256':'56f25d6c9c3947954e29689a4fbd4c2ff0c09abd6515e631311939b747d4d51d','pdf_page_one_based':19,'table':5,'row':'46-50%','percent_extinct':'30.68','percent_worse':'0.64','percent_better':'68.68','required_inputs':2500,'transcription':'Visually inspected original PDF Table5; five condition levels each with500 original deposited inputs.','implied_integer_counts':{'extinct':767,'worse':16,'better':1717}}
assert sum(Decimal(target[k]) for k in ['percent_extinct','percent_worse','percent_better'])==100
report={'condition50_counts':counts,'condition50_percentages':{k:v/5 for k,v in counts.items()},'table5_target':target,'required_conditions':list(range(46,51)),'coverage_by_condition':coverage,'completed_inputs_in_bin':sum(coverage.values()),'missing_inputs_in_bin':2500-sum(coverage.values()),'per_run_csv_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'inventory_sha256':hashlib.sha256(inventory.read_bytes()).hexdigest(),'scope':'Complete50% cohort is not the46–50% table bin. No table agreement or disagreement verdict. Paper prose puts equality in worse; deposited plotting code puts equality in better. Equality retained separately; none observed in this cohort.'}
assert counts['equal_initial']==0
(r/'coverage.json').write_text(json.dumps(report,indent=2)+'\n')
with (r/'missing-inputs.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=['entry','condition','seed']);w.writeheader();w.writerows({'entry':name,**v} for name,v in sorted(entries.items()) if name not in completed)
print(json.dumps(report,indent=2))
