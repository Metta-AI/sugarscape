from pathlib import Path
import hashlib,io,json,tarfile
root=Path('/home/dev/sugarscape/blueprints-long5000-002')
output=Path('/home/dev/sugarscape/blueprints-long5000-checkpoint-002.tar.gz')
assert not output.exists()
counts={}
with tarfile.open(output,'w:gz',compresslevel=1) as tar:
 for model in ['egoisticHalfLookaheadBinary','benthamHalfLookaheadBinary']:
  folder=root/model
  ledger=(folder/'completed.jsonl').read_bytes()
  assert ledger.endswith(b'\n')
  records=[json.loads(line) for line in ledger.splitlines()]
  assert [row['index'] for row in records]==list(range(len(records)))
  counts[model]=len(records)
  for name in ['manifest.json','run_runtime.py','source-sha256.json']:
   tar.add(folder/name,arcname=model+'/'+name)
  info=tarfile.TarInfo(model+'/completed.jsonl');info.size=len(ledger)
  tar.addfile(info,io.BytesIO(ledger))
  for row in records:
   assert row['exit_code']==0
   run=folder/row['entry'].removesuffix('.config')
   for name,digest in row['files_sha256'].items():
    path=run/name
    assert hashlib.sha256(path.read_bytes()).hexdigest()==digest
    tar.add(path,arcname=model+'/'+run.name+'/'+name)
report={'archive':str(output),'bytes':output.stat().st_size,'sha256':hashlib.sha256(output.read_bytes()).hexdigest(),'counts':counts,'scope':'Frozen completed ledger rows only; live incomplete runs excluded, no native process interrupted.'}
output.with_suffix('.receipt.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report),flush=True)
