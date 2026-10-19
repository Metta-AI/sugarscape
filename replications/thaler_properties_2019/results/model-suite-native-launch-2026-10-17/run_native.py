import hashlib,json,subprocess,tarfile,time
from pathlib import Path
r=Path('/root/sugarscape/thaler-model-suite-native-001')
m=json.loads((r/'manifest.json').read_text());p=r/'sugarscape-model-test'
assert hashlib.sha256(p.read_bytes()).hexdigest()==m['binary']['sha256']
assert not (r/'terminal.json').exists() and not (r/'model-suite.log').exists()
native=Path('/root/sugarscape/thaler-properties-observer-001/source')
for name,digest in m['source_sha256'].items():assert hashlib.sha256((native/name).read_bytes()).hexdigest()==digest
command=['timeout','--kill-after=30s',str(m['seconds']),str(p),'--quickcheck-replay='+str(m['replay_seed'])]
(r/'command.json').write_text(json.dumps(command)+'\n')
started=time.time()
with (r/'model-suite.log').open('x') as stream:result=subprocess.run(command,cwd=native,stdout=stream,stderr=subprocess.STDOUT)
(r/'terminal.json').write_text(json.dumps({'exit_code':result.returncode,'started_unix':started,'finished_unix':time.time(),'limit_seconds':m['seconds']})+'\n')
with tarfile.open(r/'complete-evidence.tar.gz','w:gz') as archive:
 for name in ['sugarscape-model-test','manifest.json','preflight.json','command.json','run_native.py','model-suite.log','terminal.json']:archive.add(r/name,arcname=name)
print((r/'terminal.json').read_text(),flush=True)
raise SystemExit(result.returncode)
