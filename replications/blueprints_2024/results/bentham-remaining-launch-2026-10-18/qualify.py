from pathlib import Path
import subprocess,json,time,signal,sys
records=[]
for name in ['input-deadline','batch-deadline','signal','complete-final']:
 command=[sys.executable,'run_selected.py','engine','blueprints-homogeneous.zip',name+'.json','qualification/'+name]
 process=subprocess.Popen(command)
 if name=='signal':time.sleep(3);process.send_signal(signal.SIGTERM)
 code=process.wait(timeout=620)
 assert code==(0 if name=='complete-final' else 124),(name,code)
 output=Path('qualification')/name
 termination=json.loads((output/'termination.json').read_text());assert not termination['remaining_live_groups']
 summary=json.loads((output/'summary.json').read_text());assert summary['complete']==(name=='complete-final')
 records.append({'condition':name,'command':command,'exit_code':code,'termination':termination,'summary':summary})
subprocess.run([sys.executable,'audit_batch.py','blueprints-homogeneous.zip','qualification/complete-final/input-60','qualification/complete-audit'],check=True)
audit=json.loads(Path('qualification/complete-audit/audit.json').read_text())
assert audit['results'][0]['trajectory_sha256']=='023589822d8eaf6a97507d9dc4642b68460742a778b623bd1c0b56c66acefb48'
Path('qualification/verified-controls.json').write_text(json.dumps(records,indent=2)+'\n')
print('Linux lifecycle controls and original trajectory parity passed',flush=True)
