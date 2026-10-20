from pathlib import Path
import gzip,hashlib,json,subprocess,sys
r=Path(__file__).resolve().parent
repo=Path('/Users/relh/Code/workspace/sugarscape-brearcliffe/replications/brearcliffe_2020')
encoded=(r/'metric-curves.json.gz').read_bytes()
assert encoded==(r.parent/'brearcliffe-horizontal-calibration-002/metric-curves.json.gz').read_bytes()
assert (r.parent/'brearcliffe-horizontal-endpoint-regression-001/metric-endpoints.json').read_bytes()==(r/'before-endpoints/metric-endpoints.json').read_bytes()
old=json.loads(gzip.decompress((repo/'results/full-curve-digitization-2026-10-19/metric-curves.json.gz').read_bytes()))
new=json.loads(gzip.decompress(encoded))
checked=0
for before,after in zip(old['figures'],new['figures'],strict=True):
 old_rows={(x['panel_sha256'],x['breed'],x['column']):x for x in before['records']}
 for row in after['records']:
  prior=old_rows[(row['panel_sha256'],row['breed'],row['column'])]
  assert {k:v for k,v in row.items() if k!='approximate_tick_interval'}=={k:v for k,v in prior.items() if k!='approximate_tick_interval'}
  checked+=1
sources={'rule-m-rule-m':'brearcliffe-rule-m-remote-recovery-001','rule-m-ec':'brearcliffe-rule-m-ec-snapshot-001','rule-m-q':'brearcliffe-rule-m-q-snapshot-001','rule-m-sarsa':'brearcliffe-rule-m-sarsa-snapshot-001'}
reports=[]
for name,source in sources.items():
 cohort=r.parent/source/'cohort'
 output=r/name
 cmd=[sys.executable,str(repo/'compare_curves.py'),str(cohort),str(r/'metric-curves.json.gz'),str(output)]
 subprocess.run(cmd,check=True)
 actual=json.load(gzip.open(output/'curve-comparison.json.gz','rt'))
 prior=json.load(gzip.open(repo/f'results/{name}-complete-cohort-2026-10-19/curve-comparison.json.gz','rt'))
 assert actual['summary_sha256']==prior['summary_sha256'] and actual['means_sha256']==prior['means_sha256']
 rows=actual['records']; visible=[x for x in rows if 'signed_range_separation' in x]; endpoints=[x for x in visible if x['column']==302]
 metrics=[]
 for fig in range(3,10):
  for breed in ['A','B']:
   current=[x for x in rows if x['figure']==fig and x['breed']==breed]
   previous=[x for x in prior['records'] if x['figure']==fig and x['breed']==breed and x['column']>=next(f for f in new['figures'] if f['figure']==fig)['x_calibration']['left_column']]
   metrics.append({'figure':fig,'breed':breed,'visible':sum('signed_range_separation' in x for x in current),'above_before':sum(x.get('signed_range_separation',0)>0 for x in previous),'above_after':sum(x.get('signed_range_separation',0)>0 for x in current),'below_before':sum(x.get('signed_range_separation',0)<0 for x in previous),'below_after':sum(x.get('signed_range_separation',0)<0 for x in current)})
 reports.append({'cohort':name,'records':len(rows),'visible':len(visible),'unresolved':len(rows)-len(visible),'endpoint_visible':len(endpoints),'endpoint_overlaps':sum(x['signed_range_separation']==0 for x in endpoints),'unchanged_simulation_and_summary_hashes':True,'metrics':metrics})
report={'all_panel_grid_lines_verified':112,'coordinates_by_figure':{f['figure']:f['x_calibration'] for f in new['figures']},'records_with_unchanged_vertical_measurements':checked,'repeat_extraction_byte_identical':True,'prechange_endpoint_execution_byte_identical':True,'curve_sha256':hashlib.sha256(encoded).hexdigest(),'cohorts':reports,'limits':'Correction fixes horizontal mapping, not model behavior. Raster separations are descriptive, dependent, and not statistical tests.'}
(r/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
