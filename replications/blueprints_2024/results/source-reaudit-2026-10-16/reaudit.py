from pathlib import Path
import json,subprocess
base=Path(__file__).resolve().parent
out=base/'blueprints-source-reaudit-001';out.mkdir()
repo=base.parent/'sugarscape-blueprints'
python=str(base.parent/'sugarscape-replications/.venv/bin/python')
archive=str(base/'papers/blueprints-homogeneous.zip')
reports=[]
for ledger in sorted(base.glob('blueprints*/completed.jsonl')):
 manifest=json.loads((ledger.parent/'manifest.json').read_text())
 if 'model' not in manifest or not ledger.read_text().splitlines():continue
 dest=out/ledger.parent.name
 command=[python,str(repo/'replications/blueprints_2024/audit_batch.py'),archive,str(ledger.parent),str(dest),'--allow-prefix']
 with (out/(ledger.parent.name+'.log')).open('w') as log:r=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT)
 assert r.returncode==0,ledger.parent
 reports.append(str(dest/'audit.json'))
 print(ledger.parent.name,flush=True)
command=[python,str(repo/'replications/blueprints_2024/reconcile_coverage.py'),archive,str(out/'coverage'),*reports]
with (out/'coverage.log').open('w') as log:r=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT)
assert r.returncode==0
print((out/'coverage.log').read_text())
