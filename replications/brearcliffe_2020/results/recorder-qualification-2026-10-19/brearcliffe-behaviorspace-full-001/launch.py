from pathlib import Path
import subprocess,time,json,shutil
r=Path(__file__).resolve().parent
assert shutil.disk_usage(r).free>2*1024**3
command=json.loads((r/'command.json').read_text())
start=time.monotonic()
with (r/'terminal.log').open('x') as log:
    result=subprocess.run(command,cwd='/Users/relh/Code/workspace/sugarscape-replication-evidence/brearcliffe-native-pilot-001',stdout=log,stderr=subprocess.STDOUT,timeout=600)
receipt={'exit_code':result.returncode,'elapsed_seconds':time.monotonic()-start,'output_bytes':sum(p.stat().st_size for p in r.rglob('*') if p.is_file()),'scope':'Full native BehaviorSpace comparator, not paper ensemble.'}
(r/'terminal.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt))
assert result.returncode==0
assert receipt['output_bytes']<52428800
