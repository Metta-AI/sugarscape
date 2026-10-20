"""Cross-check aggregate CSV analysis against independent raw-record audit summaries."""
from pathlib import Path
import json,statistics,math
base=Path('/Users/relh/Code/workspace/sugarscape-replication-evidence')
analysis=json.loads((base/'pike-phase2-analysis-001/analysis.json').read_text())
raw=json.loads((base/'pike-phase2-complete-001/reconciled/reconciliation.json').read_text())
errors=[]
for label,summary in analysis['prices'].items():
 approach,threshold=label.split('-')
 rows=[r for r in raw['runs'] if r['approach']==approach and r['threshold']==int(threshold)]
 assert len(rows)==100
 assert sum(r['undefined_dispersion_steps'] for r in rows)==summary['undefined_dispersion_steps']
 assert 100000-sum(r['price_steps'] for r in rows)==summary['no_trade_steps']
 for window in ['early','late']:
  values=[r['windows'][window] for r in rows]
  errors.append(abs(statistics.fmean(r['trades'] for r in values)-summary['windows'][window]['trades_per_run']['mean']))
  for metric in ['geometric_mean_price','sample_sd_log_price']:
   defined=[r[metric]['mean_over_defined_steps'] for r in values if r[metric]['defined_steps']>0]
   target=summary['windows'][window][metric]
   assert len(defined)==target['defined_runs']
   assert sum(r[metric]['defined_steps'] for r in values)==target['defined_steps']
   errors.append(abs(statistics.fmean(defined)-target['run_mean_interval']['mean']))
assert max(errors)<1e-10
report={'conditions':6,'windows_per_condition':2,'mean_comparisons':len(errors),'maximum_absolute_difference':max(errors),'undefined_counts_exact':True,'scope':'CSV-derived price aggregates agree with separately retained raw-record audit summaries. This does not establish paper equivalence.'}
(base/'pike-phase2-statistics-audit-001/price-audit.json').write_text(json.dumps(report,indent=2)+'\n')
print(report)
