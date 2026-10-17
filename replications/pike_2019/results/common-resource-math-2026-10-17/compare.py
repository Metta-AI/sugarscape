from pathlib import Path
import json,tarfile
r=Path(__file__).resolve().parent
local=json.loads((r/'local/trace.json').read_text());cloud=json.loads((r/'cloud-trace.json').read_text())
for field in ['python','numpy','scipy','mesa','networkx','gmean_sha256','native_agent_sha256','steps']:assert local[field]==cloud[field]
assert len(local['calls'])==len(cloud['calls'])==460
changes=[{'index':i,'local':a,'cloud':b} for i,(a,b) in enumerate(zip(local['calls'],cloud['calls'],strict=True)) if a!=b]
first=changes[0]
assert first['local']['inputs']==first['cloud']['inputs']
with tarfile.open(r.parent/'pike-common-cloud-portability-001/native.tar.gz') as t:
 original=json.load(t.extractfile('pike-common-cloud-portability-001/common-multi/prices.json'))
cloud_prices=json.loads((r/'cloud-prices.json').read_text())
assert cloud_prices['1']==original['1']
original_local=json.loads((r.parent/'pike-common-native-001/common-multi-1/prices.json').read_text())
assert json.loads((r/'local/prices.json').read_text())['1']==original_local['1']
report={'calls':460,'trades':393,'first_differing_call':first,'different_calls':len(changes),'equal_input_different_result_calls':sum(a['inputs']==b['inputs'] and a['result']!=b['result'] for a,b in zip(local['calls'],cloud['calls'],strict=True)),'trace_prices_exactly_match_uninstrumented_runs':True,'local_platform':local['platform'],'cloud_platform':cloud['platform'],'scope':'First native model step with unchanged gmean return values. Identical inputs and source produce different runtime arithmetic. This establishes an early numerical divergence, not sole causation of later group membership changes.'}
(r/'comparison.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
