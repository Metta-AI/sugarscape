from pathlib import Path
import hashlib,json,subprocess
root=Path('/root/sugarscape/thaler-properties-native-seeds-001')
plan=json.loads((root/'equivalence-plan.json').read_text())
assert hashlib.sha256(Path(plan['binary']).read_bytes()).hexdigest()==plan['binary_sha256']
for name,h in plan['source_sha256'].items():assert hashlib.sha256((Path(plan['source'])/name).read_bytes()).hexdigest()==h
for label,key in [('full','full_seed'),('normalized','normalized_seed')]:
 d=root/label;d.mkdir()
 command=[plan['binary'],'-s',plan['scenario'],'-f',str(plan['steps']),'-o',str(d/'dynamics.m'),'-r',str(plan[key])]
 (d/'command.json').write_text(json.dumps(command)+'\n')
 with (d/'stdout.log').open('wb') as out,(d/'stderr.log').open('wb') as err:
  result=subprocess.run(command,cwd=plan['source'],stdout=out,stderr=err,timeout=120)
 (d/'exit.json').write_text(json.dumps({'exit_code':result.returncode})+'\n');result.check_returncode()
assert (root/'full/dynamics.m').read_bytes()==(root/'normalized/dynamics.m').read_bytes()
(root/'equivalence.json').write_text(json.dumps({'byte_identical':True,'raw_sha256':hashlib.sha256((root/'full/dynamics.m').read_bytes()).hexdigest(),'plan':plan},indent=2)+'\n')
