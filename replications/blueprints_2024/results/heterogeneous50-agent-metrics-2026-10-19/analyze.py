from pathlib import Path
from fractions import Fraction
from decimal import Decimal
import csv,json,hashlib,tarfile,math
import fitz
r=Path(__file__).resolve().parent
repo=Path('/Users/relh/Code/workspace/sugarscape-blueprints'); source=repo/'replications/blueprints_2024/results/heterogeneous50-complete-2026-10-19/population'
summary=json.loads((source/'summary.json').read_text()); assert summary['validated_inputs']==500 and summary['condition']==50
rows=list(csv.DictReader((source/'per-run.csv').open())); wanted={x['trajectory_sha256']:x for x in rows}; assert len(wanted)==500
metrics={'meanWealth':(18,29,30,203,0,350),'agentMeanTimeToLive':(19,88,89,202,10,20),'meanAgeAtDeath':(21,192,193,207,0,70)}
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
   measurements={}
   for metric in metrics:
    values=[Fraction(x[metric]) for x in trajectory]; assert all(v>=0 for v in values)
    measurements[metric]={'initial':str(values[0]),'sum':str(sum(values)),'final':str(values[-1])}
   results[sha]={'entry':row['entry'],'seed':row['seed'],'observations':len(trajectory),'final_population':int(row['final_population']),'trajectory_sha256':sha,'measurements':measurements}
assert results.keys()==wanted.keys()
records=sorted(results.values(),key=lambda x:x['entry'])
paper=r.parent/'papers/blueprints-author-2024.pdf'; assert hashlib.sha256(paper.read_bytes()).hexdigest()=='56f25d6c9c3947954e29689a4fbd4c2ff0c09abd6515e631311939b747d4d51d'
with fitz.open(paper) as pdf: ds=pdf[17].get_drawings()
reports={}
for metric,(figure,frame_index,curve_index,count,ymin,ymax) in metrics.items():
 conventions={}
 for name in ['observed_including_initial','observed_excluding_initial','zero_extended_including_initial','zero_extended_excluding_initial']:
  exclude=name.endswith('excluding_initial'); fixed=name.startswith('zero_extended'); means=sorted((Fraction(x['measurements'][metric]['sum'])-(Fraction(x['measurements'][metric]['initial']) if exclude else 0))/((5001 if fixed else x['observations'])-exclude) for x in records); median=(means[249]+means[250])/2; conventions[name]={'median':float(median),'median_exact':str(median)}
 f=ds[frame_index]['rect']; curve=ds[curve_index]; assert curve['fill']==(1.,0.,1.) and len(curve['items'])==count and all(x[0]=='l' for x in curve['items'])
 x=(f.x0+f.x1)/2; y0=f.y0+.143;y1=f.y1-.143
 ys=[a.y+(x-a.x)/(b.x-a.x)*(b.y-a.y) for _,a,b in curve['items'] if min(a.x,b.x)<=x<max(a.x,b.x)];assert len(ys)==2
 lo,hi=sorted(ymin+(y1-y)/(y1-y0)*(ymax-ymin) for y in ys)
 reports[metric]={'conventions':conventions,'target':{'figure':figure,'page_one_based':18,'frame_index':frame_index,'median_index':curve_index,'axis_range':[ymin,ymax],'pdf_x':x,'outline_intersections_pdf_y':ys,'ink_interval':[lo,hi]},'within_paper_ink':{k:lo<=v['median']<=hi for k,v in conventions.items()}}
report={'inputs':500,'observations':sum(x['observations'] for x in records),'population_summary_sha256':hashlib.sha256((source/'summary.json').read_bytes()).hexdigest(),'metrics':reports,'scope':'Medians of per-run recorded agent metrics under declared averaging conventions; zero extension is a sensitivity convention, not observed post-extinction agent behavior. One condition only; historical plotting choices unresolved.'}
(r/'per-run.json').write_text(json.dumps(records,indent=2)+chr(10))
(r/'summary.json').write_text(json.dumps(report,indent=2)+chr(10));print(json.dumps(report,indent=2))
