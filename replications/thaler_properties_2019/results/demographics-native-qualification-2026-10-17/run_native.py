import hashlib,json,subprocess,tarfile
from pathlib import Path
root=Path('/root/sugarscape/thaler-properties-demographics-native-001')
protocol=json.loads((root/'original-protocol.json').read_text())
spec=protocol['variants']['original'];native=Path(spec['root'])
for name,digest in spec['source_sha256'].items():assert hashlib.sha256((native/'source'/name).read_bytes()).hexdigest()==digest
for name,key in [('observe','binary_sha256'),('Observe.hs','observer_sha256')]:assert hashlib.sha256((native/name).read_bytes()).hexdigest()==spec[key]
expected=json.loads((root/'expected-parity.json').read_text())
for scenario in protocol['scenarios']:
 folder=root/'parity'/scenario['key'];folder.mkdir(parents=True)
 command=[str(native/'observe'),scenario['constructor'],str(protocol['seeds'][0]),'1000','10',str(folder/'trajectory')]
 (folder/'command.json').write_text(json.dumps(command)+'\n')
 with (folder/'stdout.log').open('w') as out,(folder/'stderr.log').open('w') as err:subprocess.run(command,cwd=native,stdout=out,stderr=err,check=True,timeout=900)
 for name,digest in expected[scenario['key']].items():assert hashlib.sha256((folder/name).read_bytes()).hexdigest()==digest,(scenario['key'],name)
(root/'parity-complete.json').write_text(json.dumps({'exact_exports':10,'scenarios':['mating','inheritance']})+'\n')
with tarfile.open(root/'parity-evidence.tar.gz','w:gz') as archive:
 for name in ['parity','parity-complete.json','expected-parity.json','original-protocol.json']:archive.add(root/name,arcname=name)
result=subprocess.run(['python3',str(root/'run_demographics.py'),str(root/'protocol.json'),'original',str(root/'remaining'),'--start','28','--stop','100'],timeout=10830)
(root/'terminal.json').write_text(json.dumps({'exit_code':result.returncode})+'\n')
with tarfile.open(root/'complete-evidence.tar.gz','w:gz') as archive:
 for name in ['protocol.json','run_demographics.py','terminal.json','remaining']:archive.add(root/name,arcname=name)
raise SystemExit(result.returncode)
