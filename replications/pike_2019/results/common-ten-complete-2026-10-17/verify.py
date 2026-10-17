from pathlib import Path
import csv,json
import numpy as np
root=Path(__file__).resolve().parent
source=root/'native/pike-common-cloud-final-export-001/audit'
reconciled=root/'reconciled'
with (reconciled/'price-measurements.csv').open() as stream:
    combined={(r['variant'],int(r['numpy_seed']),int(r['step'])):r for r in csv.DictReader(stream)}
assert len(combined)==200000
with (source/'price-measurements.csv').open() as stream:
    count=0
    for row in csv.DictReader(stream):
        assert combined[row['variant'],int(row['numpy_seed']),int(row['step'])]==row
        count+=1
assert count==198000
maximum=0.0
for variant in ['common-one','common-multi']:
    prices=json.loads((root.parent/'pike-common-cloud-zero-001/extracted/pike-common-cloud-zero-001'/variant/'prices.json').read_text())
    for step in range(1,1001):
        values=prices[str(step)] if str(step) in prices else []
        row=combined[variant,0,step]
        assert int(row['trades'])==len(values)
        for metric,defined in [('geometric_mean_price',len(values)>0),('sample_sd_log_price',len(values)>1)]:
            if not defined:
                assert row[metric]==''
                continue
            logs=np.log(values)
            expected=float(np.exp(logs.mean())) if metric=='geometric_mean_price' else float(logs.std(ddof=1))
            actual=float(row[metric]);assert np.isclose(actual,expected,rtol=1e-12,atol=1e-12)
            maximum=max(maximum,abs(actual-expected))
r=json.loads((reconciled/'reconciliation.json').read_text())
assert len(r['runs'])==200 and r['numerically_failed_runs']==sum(x['nonfinite_health_records']>0 for x in r['runs'])
a={'unchanged_batch_step_records':count,'independently_reconstructed_zero_step_records':2000,'max_absolute_zero_statistic_error':maximum,'numeric_failure_count':r['numerically_failed_runs'],'scope':'Checks all198000 previously audited CSV records unchanged after reconciliation; independently reconstructs both seedzero1000step price histories using NumPy. Rawhealth audits remain separate evidence.'}
(root/'verification.json').write_text(json.dumps(a,indent=2)+'\n')
print(json.dumps(a))
