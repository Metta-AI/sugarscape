from pathlib import Path
from fractions import Fraction
import json,csv,hashlib
import fitz,numpy as np
r=Path(__file__).resolve().parent
paper=r.parent/'papers/blueprints-author-2024.pdf'; pin=hashlib.sha256(paper.read_bytes()).hexdigest(); assert pin=='56f25d6c9c3947954e29689a4fbd4c2ff0c09abd6515e631311939b747d4d51d'
with fitz.open(paper) as pdf: drawings=pdf[16].get_drawings()
frame=drawings[29]['rect']; x0,y0,x1,y1=frame.x0+.143,frame.y0+.143,frame.x1-.143,frame.y1-.143
x=(x0+x1)/2; targets={}
for name,index,count in [('q25',33,381),('q75',42,389)]:
 d=drawings[index]; assert d['fill']==(0.,0.,0.) and len(d['items'])==count and all(i[0]=='l' for i in d['items'])
 ys=[a.y+(x-a.x)/(b.x-a.x)*(b.y-a.y) for _,a,b in d['items'] if min(a.x,b.x)<=x<max(a.x,b.x)]
 target={'drawing_index':index,'outline_intersections_pdf_y':sorted(ys),'status':'unresolved-dash-gap'}
 if ys: target.update(status='visible-outline-envelope',population_ink_envelope=[(y1-max(ys))/(y1-y0)*1400,(y1-min(ys))/(y1-y0)*1400])
 targets[name]=target
assert targets['q25']['status']=='unresolved-dash-gap'; assert len(targets['q75']['outline_intersections_pdf_y'])==4
source=r.parent/'blueprints-heterogeneous50-population-001/per-run.csv'; rows=list(csv.DictReader(source.open())); assert len(rows)==len({x['entry'] for x in rows})==500
methods=['inverted_cdf','averaged_inverted_cdf','closest_observation','interpolated_inverted_cdf','hazen','weibull','linear','median_unbiased','normal_unbiased']; result={}
for name in ['observed_including_initial','observed_excluding_initial','zero_extended_including_initial','zero_extended_excluding_initial']:
 exclude=name.endswith('excluding_initial'); fixed=name.startswith('zero_extended'); values=sorted(Fraction(int(x['population_sum'])-250*exclude,(5001 if fixed else int(x['observations']))-exclude) for x in rows)
 exact=[]
 for q in [Fraction(1,4),Fraction(3,4)]:
  position=499*q; j=position.numerator//position.denominator; weight=position-j; exact.append(values[j]*(1-weight)+values[j+1]*weight)
 array=np.array([float(x) for x in values]); methods_values={m:np.quantile(array,[.25,.75],method=m).tolist() for m in methods}
 assert np.allclose(methods_values['linear'],[float(v) for v in exact],rtol=0,atol=1e-12)
 lo,hi=targets['q75']['population_ink_envelope']; overlap={m:lo<=v[1]<=hi for m,v in methods_values.items()}; assert all(overlap.values())
 result[name]={'type7_exact':[str(v) for v in exact],'quantiles_by_method':methods_values,'upper_quartile_within_ink':overlap,'lower_quartile_paper_comparison':'unresolved-dash-gap'}
report={'paper_sha256':pin,'figure':16,'pdf_page_one_based':17,'utilitarian_percent':50,'pdf_x':x,'targets':targets,'per_run_csv_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'numpy_version':np.__version__,'conventions':result,'limits':['Only one completed condition, no whole-paper verdict.','Lower quartile has no ink at exact x50; no interpolation or comparison assigned.','Upper envelope bounds four outline intersections, not a confidence interval.','Frame calibration uncertainty remains; historical quantile method unknown.','Nine quantile definitions and four averaging conventions are sensitivity checks, not independent experiments.']}
(r/'quartiles.json').write_text(json.dumps(report,indent=2)+'\n'); print(json.dumps({'targets':targets,'type7':{k:v['type7_exact'] for k,v in result.items()}},indent=2))
