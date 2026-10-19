from pathlib import Path
import json
import tarfile
import hashlib
root=Path('/root/sugarscape/need-for-greed-baseline-recovery-001')
receipts=sorted(root.joinpath('logs').glob('*.receipt.json'))
records=[json.loads(p.read_bytes()) for p in receipts]
assert records and all(r['verified'] for r in records)
out=root/'audit-prefix-001.tar.gz'
with tarfile.open(out,'x:gz') as tar:
 for name in ('plan.json','run_native.py','source-sha256.json','run_recovery.py','bootstrap.sh'):
  tar.add(root/name,arcname=name)
 for row in records:
  entry=row['entry']
  name='runs/'+entry.removesuffix('.config')
  tar.add(root/name,arcname=name)
  for suffix in ('.log','.receipt.json'):
   name='logs/'+entry+suffix
   tar.add(root/name,arcname=name)
print(json.dumps({'archive':str(out),'bytes':out.stat().st_size,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'inputs':len(records)}))
