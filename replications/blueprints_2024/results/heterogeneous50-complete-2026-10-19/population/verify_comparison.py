from pathlib import Path
from fractions import Fraction
import csv,json,hashlib
import numpy as np
r=Path(__file__).resolve().parent
repeat=r.parent/'blueprints-heterogeneous50-population-repeat-001'
for name in ['summary.json','per-run.csv']: assert (r/name).read_bytes()==(repeat/name).read_bytes()
s=json.loads((r/'summary.json').read_text()); rows=list(csv.DictReader((r/'per-run.csv').open())); assert len(rows)==len({x['entry'] for x in rows})==len({x['seed'] for x in rows})==500
checks={}
for name,c in s['conventions'].items():
 exclude=name.endswith('excluding_initial'); fixed=name.startswith('zero_extended')
 fractions=[Fraction(int(x['population_sum'])-(250 if exclude else 0),(5001 if fixed else int(x['observations']))-int(exclude)) for x in rows]
 values=np.array([float(x) for x in fractions]); order=np.argsort(values); selected=[fractions[int(order[j])] for j in (249,250)]
 exact=(selected[0]+selected[1])/2; assert exact==Fraction(c['median_exact'])
 m=float(np.median(values)); rounding=abs(m-float(exact)); assert rounding<=np.spacing(m)
 checks[name]={'numpy_median':m,'exact_median':str(exact),'absolute_rounding_difference':rounding,'float_spacing':float(np.spacing(m))}
p=Path('/Users/relh/Code/workspace/sugarscape-blueprints/replications/blueprints_2024/results/heterogeneous-figure16-target-2026-10-19/target.json'); target=json.loads(p.read_text())['selected_factor']; lo,hi=target['population_ink_lower'],target['population_ink_upper']; assert all(lo<=c['median']<=hi for c in s['conventions'].values())
report={'inputs':500,'observations':sum(int(x['observations']) for x in rows),'native_extinctions':sum(int(x['final_population'])==0 for x in rows),'numpy_version':np.__version__,'checks':checks,'repeat_outputs_byte_identical':True,'paper_target_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'paper_ink_interval':[lo,hi],'all_four_medians_within_paper_ink':True,'scope':'Independent NumPy ordering selects the exact rational middle pair; floating arithmetic differs by at most one ULP. One complete condition shows graphical agreement under four conventions, not equivalence or full-paper reproduction.'}
(r/'comparison.json').write_text(json.dumps(report,indent=2)+'\n'); print(json.dumps(report,indent=2))
