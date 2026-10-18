from pathlib import Path
import tarfile,xml.etree.ElementTree as ET,json,subprocess,hashlib,math
root=Path(__file__).parent
original=root.parent/'openabl-gpu-qualification-001'
repo=Path('/Users/relh/Code/workspace/sugarscape-openabl/replications/openabl_2021')
records={};observations=0
for label,archive,prefix in [('native',original/'successful-build-evidence.tar.gz','generated'),('repeat',root/'repeat-002.tar.gz','native-repeat-002'),('ordered',root/'native-evidence.tar.gz','generated')]:
 output=root/(label+'-audit002');output.mkdir()
 snapshots=[]
 with tarfile.open(archive) as tar:
  for step in range(101):
   tree=ET.fromstring(tar.extractfile(f'{prefix}/iterations/{step}.xml').read());assert int(tree.findtext('itno'))==step
   rows=[]
   for a in tree.findall('xagent'):
    assert a.findtext('name')=='Agent'
    row={'pos':[float(a.findtext(k)) for k in ['x','y']],'target_pos':[float(a.findtext(k)) for k in ['target_pos_x','target_pos_y']]}
    row.update({k:int(a.findtext(k)) for k in ['agent_id','state','sugar_level','metabolism','env_sugar_level','max_env_sugar_level']});rows.append(row)
    assert row['state'] in range(4) and 0<=row['env_sugar_level']<=row['max_env_sugar_level']
    assert all(math.isfinite(v) for v in row['pos']+row['target_pos'])
   rows.sort(key=lambda a:a['pos']);assert len(rows)==225 and len({tuple(a['pos']) for a in rows})==225
   if step==0:initial=rows
   assert [(a['pos'],a['max_env_sugar_level']) for a in rows]==[(a['pos'],a['max_env_sugar_level']) for a in initial]
   snapshots.append(rows);observations+=225
   (output/f'{step}.json').write_text(json.dumps({'Agent':rows})+'\n')
 records[label]=snapshots
assert records['native'][0]==records['repeat'][0]==records['ordered'][0]
audit=root/'ordered-replay';audit.mkdir();commands=[]
for step in range(1,101):
 command=['python3',str(repo/'replay.py'),str(root/'ordered-audit002'/f'{step-1}.json'),str(root/'ordered-audit002'/f'{step}.json'),str(audit/f'{step}.json'),'--steps','1','--buffer','copy']
 p=subprocess.run(command,capture_output=True,text=True);commands.append({'command':command,'exit_code':p.returncode,'stdout':p.stdout,'stderr':p.stderr})
(root/'replay-commands.json').write_text(json.dumps(commands,indent=2)+'\n')
differences={}
for left,right in [('native','repeat'),('native','ordered')]:
 differences[left+'-vs-'+right]=[sum(a[k]!=b[k] for a,b in zip(records[left][step],records[right][step],strict=True) for k in a) for step in range(101)]
result={'snapshots':303,'agent_observations':observations,'same_initial_state':True,'ordered_transition_fields_compared':180000,'ordered_transition_failures':[i+1 for i,p in enumerate(commands) if p['exit_code']!=0],'field_differences_by_step':differences,'replay_source_sha256':hashlib.sha256((repo/'replay.py').read_bytes()).hexdigest(),'completed_study':False}
(root/'audit.json').write_text(json.dumps(result,indent=2)+'\n')
print({k:v for k,v in result.items() if k!='field_differences_by_step'})
print({k:{'first_differing_step':next((i for i,n in enumerate(v) if n),None),'final_differences':v[-1]} for k,v in differences.items()})
assert not result['ordered_transition_failures']
