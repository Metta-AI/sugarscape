from pathlib import Path
from fractions import Fraction
from decimal import Decimal
import csv,json,hashlib,tarfile,math
import statistics
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
   definitions={}
   for numerator,fields in [('starvation_combat',['agentStarvationDeaths','agentCombatDeaths']),('all_reported_causes',['agentStarvationDeaths','agentCombatDeaths','agentDiseaseDeaths','agentAgingDeaths'])]:
    for exclude in [False,True]:
     selected=trajectory[int(exclude):]; positive=[x for x in selected if x['population']>0]
     assert all(all(int(x[k])==x[k] and x[k]>=0 for k in fields) for x in selected)
     deaths=[sum(x[k] for k in fields) for x in positive]; pops=[x['population'] for x in positive]; assert positive
     prefix=numerator+('/exclude_initial' if exclude else '/include_initial')
     definitions[prefix]={'positive_rows':len(positive),'zero_population_rows':len(selected)-len(positive),'deaths_at_zero_population':sum(sum(x[k] for k in fields) for x in selected if x['population']==0),'deaths_sum_positive':sum(deaths),'population_sum_positive':sum(pops),'sum_step_ratios':math.fsum(float(d)/float(p) for d,p in zip(deaths,pops))}
   results[sha]={'entry':row['entry'],'seed':row['seed'],'observations':len(trajectory),'trajectory_sha256':sha,'definitions':definitions}
assert results.keys()==wanted.keys()
records=sorted(results.values(),key=lambda x:x['entry']); definitions={}
for key in records[0]['definitions']:
 for order in ['mean_of_step_ratios','ratio_of_sums']:
  values=[]
  for row in records:
   z=row['definitions'][key]
   values.append(100*(z['sum_step_ratios']/z['positive_rows'] if order=='mean_of_step_ratios' else z['deaths_sum_positive']/z['population_sum_positive']))
  definitions[key+'/'+order]={'median_percent':statistics.median(values)}
paper=r.parent/'papers/blueprints-author-2024.pdf'; assert hashlib.sha256(paper.read_bytes()).hexdigest()=='56f25d6c9c3947954e29689a4fbd4c2ff0c09abd6515e631311939b747d4d51d'
with fitz.open(paper) as pdf: ds=pdf[17].get_drawings()
f=ds[139]['rect'];curve=ds[140];assert curve['fill']==(1.,0.,1.) and len(curve['items'])==209
x=(f.x0+f.x1)/2;y0=f.y0+.143;y1=f.y1-.143
ys=[a.y+(x-a.x)/(b.x-a.x)*(b.y-a.y) for _,a,b in curve['items'] if min(a.x,b.x)<=x<max(a.x,b.x)];assert len(ys)==2
lo,hi=sorted((y1-y)/(y1-y0)*30 for y in ys)
for definition in definitions.values():definition['within_paper_ink']=lo<=definition['median_percent']<=hi
report={'inputs':500,'observations':sum(x['observations'] for x in records),'figure20_target':{'page_one_based':18,'frame_index':139,'median_index':140,'axis_percent':[0,30],'pdf_x':x,'intersections_pdf_y':ys,'ink_percent_interval':[lo,hi]},'definitions':definitions,'zero_population_observations':sum(x['definitions']['starvation_combat/include_initial']['zero_population_rows'] for x in records),'scope':'Diagnostic of two numerator definitions and two temporal aggregation orders, with/without initial row. All use positive-population rows; zero-population deaths retained separately, not divided by zero. Historical Figure20 plotting implementation unresolved; no whole-paper verdict.'}
(r/'per-run.json').write_text(json.dumps(records,indent=2)+chr(10));(r/'summary.json').write_text(json.dumps(report,indent=2)+chr(10));print(json.dumps(report,indent=2))
