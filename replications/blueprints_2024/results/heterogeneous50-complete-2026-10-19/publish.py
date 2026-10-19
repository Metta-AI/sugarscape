from pathlib import Path
import hashlib,json,shutil,subprocess,tarfile
r=Path(__file__).resolve().parent
work=Path('/Users/relh/Code/workspace/sugarscape-blueprints')
root=work/'replications/blueprints_2024'
previous=root/'results/heterogeneous50-nineteenth-prefix-2026-10-19'
current=root/'results/heterogeneous50-complete-2026-10-19'
assert json.loads((r/'audit-terminal.json').read_text())['exit_code']==0
hashes=json.loads((r/'remote-hashes.json').read_text())
assert hashes['exit_code']==0
for line in hashes['stdout'].splitlines():
    digest,name=line.split()
    assert hashlib.sha256((r/Path(name).name).read_bytes()).hexdigest()==digest
archive=r/'terminal-evidence.tar.gz'
assert archive.stat().st_size==9386515
assert hashlib.sha256(archive.read_bytes()).hexdigest()=='4d1102ad108537198e08fbbbc148d2119b874c128be3e265740337641ff96488'
readback=r/'readback'; readback.mkdir()
with tarfile.open(r/'verified.tar.gz') as tar:
    tar.extractall(readback,filter='data')
verified=readback/'verified'
validation=json.loads((verified/'validation.json').read_text())
assert validation['auditor_sha256']==hashlib.sha256((root/'audit_supplement.py').read_bytes()).hexdigest()
for p in (verified/'audits-1').glob('*/audit.json'):
    assert p.read_bytes()==(verified/'audits-2'/p.parent.name/'audit.json').read_bytes()
current.mkdir()
shutil.copytree(verified/'audits-1',current/'audits-final')
for src,dst in [('validation.json','remote-readback-validation.json'),('members.json','members-final.json')]:
    shutil.copy2(verified/src,current/dst)
for name in ['verify.py','audit-terminal.json','remote-hashes.json','import-request.json','import-status.json','terminal-evidence.tar.gz']:
    shutil.copy2(r/name,current/name)
exports=r.parent/'storage-handoff-20261017-001/blueprints-heterogeneous50-batch-001'
for kind in ['intent','status','submission']:
    shutil.copy2(exports/f'terminal-evidence.tar.gz.{kind}.json',current/f'export-final-{kind}.json')
cmd=json.loads((previous/'inventory-command.json').read_text())
cmd[3]=str((current/'inventory').relative_to(work))
cmd += ['--completed-source',str((current/'audits-final').relative_to(work)),str((current/'terminal-evidence.tar.gz').relative_to(work))]
(current/'inventory-command.json').write_text(json.dumps(cmd,indent=2)+'\n')
with (r/'inventory.log').open('w') as log:
    subprocess.run(cmd,cwd=work,stdout=log,stderr=subprocess.STDOUT,check=True)
old=json.loads((previous/'inventory/inventory.json').read_text())
new=json.loads((current/'inventory/inventory.json').read_text())
old_rows={(x['experiment'],x['entry']):x for x in old['excluded_controls']}
new_rows={(x['experiment'],x['entry']):x for x in new['excluded_controls']}
assert len(old_rows)==982 and len(new_rows)==1006
assert all(new_rows[k]==v for k,v in old_rows.items())
assert new['remaining_inputs']==98994
condition=next(x for x in new['conditions'] if x['experiment']=='heterogeneous' and x['condition']==50)
assert condition['required']==500 and condition['remaining']==0
audits=[json.loads(p.read_text())['validated'] for p in (current/'audits-final').glob('*/audit.json')]
assert len(audits)==24
assert {(x['experiment'],x['entry']) for x in audits}==new_rows.keys()-old_rows.keys()
summary={'new_inputs':24,'new_observations':sum(x['observations'] for x in audits),'full_5000_steps':sum(x['final_timestep']==5000 for x in audits),'native_extinctions':sum(x['final_population']==0 for x in audits),'completed_unique_inputs':1006,'remaining_inputs':98994,'condition050_completed':500,'condition050_required':500,'previous_inputs_preserved_exactly':982,'scope':'All500 original heterogeneous50 inputs audited; full-condition population analysis and paper comparison remain separate.'}
(current/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))
