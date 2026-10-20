from pathlib import Path
import csv,hashlib,json,shutil,subprocess,sys,tarfile,time
root=Path(__file__).resolve().parent
node='relh-sugarscape-runtime-memory-cpu8-20261018-v1'
cmd=json.loads((root/'submission.json').read_text())['command_id']
deadline=time.monotonic()+900
while True:
    states=json.loads(subprocess.check_output(['autor','ps',node,'--json'],text=True,timeout=30))
    state=next(x for x in states['items'] if x['command_id']==cmd)
    (root/'collector-state.json').write_text(json.dumps(state,indent=2)+'\n')
    if state['state']=='exited':
        assert state['exit_code']==0
        break
    assert state['state']=='running' and time.monotonic()<deadline
    time.sleep(20)
for name in ['snapshot.json','evidence.tar.gz']:
    p=subprocess.run(['autor','cp',node+':/root/sugarscape/'+root.name+'/'+name,str(root/name),'--json'],capture_output=True,text=True,timeout=180)
    (root/(name+'-download.json')).write_text(json.dumps({'exit_code':p.returncode,'stdout':p.stdout,'stderr':p.stderr},indent=2)+'\n');assert p.returncode==0
snapshot=json.loads((root/'snapshot.json').read_text());archive=root/'evidence.tar.gz'
assert archive.stat().st_size==snapshot['bytes'] and hashlib.sha256(archive.read_bytes()).hexdigest()==snapshot['sha256']
assert shutil.disk_usage(root).free>256*1024**2
extracted=root/'readback';extracted.mkdir()
with tarfile.open(archive) as tar:
    for member in tar.getmembers():
        assert not Path(member.name).is_absolute() and '..' not in Path(member.name).parts
        assert member.isfile() or member.isdir()
    tar.extractall(extracted,filter='data')
repo=Path('/Users/relh/Code/workspace/sugarscape-brearcliffe/replications/brearcliffe_2020')
old=json.loads((root.parent/'brearcliffe-ec-rule-m-snapshot-001/union-audit/audit.json').read_text())
run=extracted/'run'
with (root/'audit.log').open('w') as log:
    subprocess.run([sys.executable,str(repo/'audit_ensemble.py'),str(root.parent/'brearcliffe-ensemble-preparation-001'),str(root/'union-audit'),*[x['directory'] for x in old['completed']],str(run)],stdout=log,stderr=subprocess.STDOUT,timeout=300,check=True)
new=json.loads((root/'union-audit/audit.json').read_text());by_id={x['run_id']:x for x in new['completed']}
assert len(by_id)==253 and all(by_id[x['run_id']]==x for x in old['completed'])
plan=json.loads((root/'protocol.json').read_text());reference=Path(by_id[plan['reference_run_id']]['directory'])/'trajectory.csv'
assert hashlib.sha256(reference.read_bytes()).hexdigest()==plan['reference_trajectory_sha256']
a=(run/'trajectory.csv').read_bytes();b=reference.read_bytes()
with (run/'trajectory.csv').open() as f:actual=list(csv.DictReader(f))
with reference.open() as f:expected=list(csv.DictReader(f))
assert len(actual)==len(expected)==20001 and len(actual[0])==17
mismatches=sum(float(a[field])!=float(b[field]) for a,b in zip(actual,expected,strict=True) for field in a if field!='tick')
report={'completed_inputs':253,'previous_inputs_preserved_exactly':252,'observations':new['observations'],'compared_observations':20001,'compared_fields':320016,'numeric_mismatches':mismatches,'exact_trajectory_bytes':a==b,'reference_run_id':plan['reference_run_id'],'paper_table_run_id':plan['run_id'],'trajectory_sha256':hashlib.sha256(a).hexdigest(),'scope':'One native paired parameter control; no credit for unexecuted inputs or paper completion.'}
(root/'validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
