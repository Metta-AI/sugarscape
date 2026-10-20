from pathlib import Path
import json,gzip,shutil
root=Path(__file__).resolve().parent
assert json.loads((root/'analysis-terminal.json').read_text())['exit_code']==0
repo=Path('/Users/relh/Code/workspace/sugarscape-brearcliffe/replications/brearcliffe_2020')
summary=json.loads((root/'cohort/summary.json').read_text())
comparison=json.loads(gzip.decompress((root/'comparison/curve-comparison.json.gz').read_bytes()))
endpoints=[]
for stat in summary['endpoint_statistics']:
 records=[r for r in comparison['records'] if r['metric']==stat['metric']]
 r=max(records,key=lambda r:r['column'])
 item={**stat,'paper_status':r['status']}
 if 'signed_range_separation' in r:
  item.update(paper_raster_interval=r['metric_interval'],cohort_range_over_x_interval=r['cohort_mean_range_over_tick_interval'],signed_range_separation=r['signed_range_separation'])
 endpoints.append(item)
visible=sum('signed_range_separation' in r for r in comparison['records'])
endpoint_visible=sum('signed_range_separation' in r for r in endpoints)
overlaps=sum(r['signed_range_separation']==0 for r in endpoints if 'signed_range_separation' in r)
report={'pairing':'Q / Q','runs':50,'observations':1000050,'visible_curve_records':visible,'unresolved_curve_records':len(comparison['records'])-visible,'endpoint_range_overlaps':overlaps,'endpoint_visible':endpoint_visible,'endpoint_unresolved':14-endpoint_visible,'endpoint_records':endpoints,'scope':'Descriptive comparison with corrected horizontal calibration; no equivalence or whole-paper verdict.'}
(root/'comparison-summary.json').write_text(json.dumps(report,indent=2)+'\n')
result=repo/'results/q-q-complete-cohort-2026-10-19'; result.mkdir()
for name in ['analysis-terminal.json','collector-state.json','disk-preflight.json','submission.json','snapshot.json','validation.json','r-validation.json','r-validation.log','readback.log','snapshot.py','readback.py','collect_analyze.py','comparison-summary.json','publish.py']:
 shutil.copyfile(root/name,result/name)
for src,dst in [('union-audit/audit.json','audit.json'),('cohort/summary.json','cohort-summary.json'),('comparison/curve-comparison.json.gz','curve-comparison.json.gz')]:
 shutil.copyfile(root/src,result/dst)
for name in ['means.csv','sample-sd.csv']:
 (result/(name+'.gz')).write_bytes(gzip.compress((root/'cohort'/name).read_bytes(),mtime=0))
shutil.copyfile(root/'cohort/bootstrap-indices.u8.gz',result/'bootstrap-indices.u8.gz')
print(json.dumps({k:v for k,v in report.items() if k!='endpoint_records'},indent=2))
print(json.dumps([r for r in endpoints if 'signed_range_separation' in r and r['signed_range_separation']!=0],indent=2))
