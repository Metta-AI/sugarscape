from pathlib import Path
import json,hashlib,tarfile
root=Path('/root/sugarscape/need-for-greed-baseline-recovery-002')
out=Path(__file__).resolve().parent
seeds=[2483216780622132986, 2513573707559938025, 2633622880550445485, 2776046745237740637, 2894409412357526145]
entries=[f'benthamHalfLookaheadBinary{s}.config' for s in seeds]
for e in entries:
 receipt=json.loads((root/'logs'/(e+'.receipt.json')).read_bytes())
 assert receipt['exit_code']==0 and receipt['verified'] is True
 assert json.loads((root/'runs'/e.removesuffix('.config')/'terminal.json').read_bytes())['exit_code']==0
archive=out/'five-completed.tar.gz'
with tarfile.open(archive,'x:gz') as tar:
 for name in ('plan.json','run_native.py','source-sha256.json','run_recovery.py','bootstrap.sh','failed-prefix.partial.gz'):
  tar.add(root/name,arcname=name)
 for e in entries:
  tar.add(root/'runs'/e.removesuffix('.config'),arcname='runs/'+e.removesuffix('.config'))
  for suffix in ('.log','.receipt.json'):tar.add(root/'logs'/(e+suffix),arcname='logs/'+e+suffix)
report={'archive_bytes':archive.stat().st_size,'archive_sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'entries':entries,'scope':'Immutable completed-input snapshot only; no simulation restart. Future regular checkpoints may contain these inputs and require exact deduplication.'}
(out/'snapshot.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))
