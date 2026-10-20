from pathlib import Path
import csv,hashlib,json,subprocess,sys,tarfile
root=Path(__file__).resolve().parent
plan=json.loads((root/'protocol.json').read_text())
main=root.parent/'brearcliffe-existing-host-ensemble-001'
assets=root.parent/'brearcliffe-existing-host-qualification-001/payload'
with (main/'payload/assignment.csv').open() as f:
    assert plan['run_id'] not in {r['run_id'] for r in csv.DictReader(f)}
cmd=[sys.executable,str(main/'payload/run_ensemble_input.py'),str(main/'prepared'),plan['run_id'],str(assets/'assets'),str(assets/'app'),str(root/'run'),'--java','/usr/bin/java','--timeout-seconds',str(plan['run_seconds'])]
(root/'command.json').write_text(json.dumps(cmd,indent=2)+'\n')
subprocess.run(cmd,check=True)
subprocess.run([sys.executable,str(main/'payload/audit_ensemble.py'),str(main/'prepared'),str(root/'audit'),str(root/'run')],check=True)
p=root/'run/trajectory.csv'
comparison={'run_id':plan['run_id'],'reference_run_id':plan['reference_run_id'],'expected_sha256':plan['reference_trajectory_sha256'],'actual_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size,'exact_sha256_match':hashlib.sha256(p.read_bytes()).hexdigest()==plan['reference_trajectory_sha256'],'scope':'Native parameter-interpretation control; one input only.'}
(root/'comparison.json').write_text(json.dumps(comparison,indent=2)+'\n')
with tarfile.open(root/'evidence.tar.gz','x:gz') as tar:
    for name in ['run','audit','protocol.json','command.json','comparison.json','run.py']:
        tar.add(root/name,arcname=name)
archive=root/'evidence.tar.gz'
report={'bytes':archive.stat().st_size,'sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'comparison':comparison}
(root/'snapshot.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
