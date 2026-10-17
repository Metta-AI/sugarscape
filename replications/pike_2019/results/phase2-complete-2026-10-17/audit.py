from pathlib import Path
import hashlib,json,subprocess,tarfile,time
root=Path(__file__).resolve().parent
receipt=json.loads((root/'export.json').read_text())
archive=root/'native.tar.gz'
assert archive.stat().st_size==receipt['bytes']
assert hashlib.sha256(archive.read_bytes()).hexdigest()==receipt['sha256']
download=root/'download';download.mkdir()
with tarfile.open(archive) as bundle:bundle.extractall(download,filter='data')
command=json.loads((root.parent/'pike-cloud-checkpoint-002/commands.json').read_text())[0]
command[3]=str(root/'reconciled')
command.append('--require-complete')
for name,start in [('phase2-62-331',274),('phase2-331-600',540)]:
 command.extend(['--segment',str(download/name),str(start),'/root/sugarscape/pike-remaining-001/'+name])
(root/'command.json').write_text(json.dumps(command,indent=2)+'\n')
started=time.time()
result=subprocess.run(command)
(root/'exit.json').write_text(json.dumps({'exit_code':result.returncode,'elapsed_seconds':time.time()-started})+'\n')
assert result.returncode==0
report=json.loads((root/'reconciled/reconciliation.json').read_text())
assert report['complete_grid'] and report['validated_runs']==600 and not report['missing_ordinals']
print(json.dumps({key:report[key] for key in ['validated_runs','complete_grid','health_records','price_step_records']}))
