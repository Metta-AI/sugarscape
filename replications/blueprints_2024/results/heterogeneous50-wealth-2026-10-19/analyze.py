from pathlib import Path
from fractions import Fraction
from decimal import Decimal
import csv,json,hashlib,tarfile,math
import fitz
r=Path(__file__).resolve().parent
repo=Path('/Users/relh/Code/workspace/sugarscape-blueprints'); source=repo/'replications/blueprints_2024/results/heterogeneous50-complete-2026-10-19/population'
summary=json.loads((source/'summary.json').read_text()); assert summary['validated_inputs']==500 and summary['condition']==50
rows=list(csv.DictReader((source/'per-run.csv').open())); wanted={x['trajectory_sha256']:x for x in rows}; assert len(wanted)==500
results={}
for archive,pin in summary['native_archive_sha256'].items():
 p=repo/archive; assert hashlib.sha256(p.read_bytes()).hexdigest()==pin
 with tarfile.open(p,'r|gz') as tar:
  for m in tar:
   if not m.name.endswith('/trajectory.json'): continue
   raw=tar.extractfile(m).read(); sha=hashlib.sha256(raw).hexdigest()
   if sha not in wanted: continue
   assert sha not in results; row=wanted[sha]; trajectory=json.loads(raw,parse_float=Decimal); assert len(trajectory)==int(row['observations'])
   assert [x['timestep'] for x in trajectory]==list(range(len(trajectory)))
   assert sum(x['population'] for x in trajectory)==int(row['population_sum'])
   values=[Fraction(x['agentWealthTotal']) for x in trajectory]; assert all(v>=0 for v in values)
   if int(row['final_population'])==0: assert values[-1]==0
   results[sha]={'entry':row['entry'],'seed':row['seed'],'observations':len(trajectory),'initial_wealth':str(values[0]),'wealth_sum':str(sum(values)),'final_population':int(row['final_population']),'trajectory_sha256':sha}
assert results.keys()==wanted.keys()
records=sorted(results.values(),key=lambda x:x['entry']); conventions={}
for name in ['observed_including_initial','observed_excluding_initial','zero_extended_including_initial','zero_extended_excluding_initial']:
 exclude=name.endswith('excluding_initial'); fixed=name.startswith('zero_extended'); means=sorted((Fraction(x['wealth_sum'])-(Fraction(x['initial_wealth']) if exclude else 0))/((5001 if fixed else x['observations'])-exclude) for x in records); median=(means[249]+means[250])/2; conventions[name]={'median':float(median),'median_exact':str(median)}
paper=r.parent/'papers/blueprints-author-2024.pdf'; assert hashlib.sha256(paper.read_bytes()).hexdigest()=='56f25d6c9c3947954e29689a4fbd4c2ff0c09abd6515e631311939b747d4d51d'
with fitz.open(paper) as pdf: ds=pdf[16].get_drawings()
f=ds[84]['rect']; curve=ds[85]; assert curve['fill']==(1.,0.,1.) and len(curve['items'])==210 and all(x[0]=='l' for x in curve['items'])
x=(f.x0+f.x1)/2; y0=f.y0+.143;y1=f.y1-.143
ys=[a.y+(x-a.x)/(b.x-a.x)*(b.y-a.y) for _,a,b in curve['items'] if min(a.x,b.x)<=x<max(a.x,b.x)];assert len(ys)==2
lo,hi=sorted((y1-y)/(y1-y0)*160000 for y in ys)
report={'inputs':500,'observations':sum(x['observations'] for x in records),'metric':'agentWealthTotal','population_summary_sha256':hashlib.sha256((source/'summary.json').read_bytes()).hexdigest(),'conventions':conventions,'figure17_target':{'page_one_based':17,'frame_index':84,'median_index':85,'utilitarian_percent':50,'pdf_x':x,'outline_intersections_pdf_y':ys,'wealth_ink_interval':[lo,hi]},'within_paper_ink':{k:lo<=v['median']<=hi for k,v in conventions.items()},'scope':'Median of per-run recorded total-agent-wealth means under four declared averaging conventions. One condition only; exact historical averaging and quantile conventions remain unresolved. Graphical ink bounds are not confidence intervals.'}
with (r/'per-run.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=list(records[0]));w.writeheader();w.writerows(records)
(r/'summary.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
