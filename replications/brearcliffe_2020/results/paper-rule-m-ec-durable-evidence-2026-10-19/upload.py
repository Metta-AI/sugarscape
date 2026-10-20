from pathlib import Path
import json,subprocess,hashlib
r=Path(__file__).resolve().parent
manifest=json.loads((r/'manifest.json').read_text())
prefix='relh-sugarscape-evidence-20261017/brearcliffe-durable-evidence-011/'
items=[(x['local_source'],x['name']) for x in manifest['archives']]+[(str(r/'manifest.json'),'manifest.json')]
receipts=[]
for path,name in items:
    p=subprocess.run(['autor','storage','cp',path,prefix+name,'--json'],capture_output=True,text=True,timeout=180)
    receipt={'source':path,'destination':'s3://'+prefix+name,'exit_code':p.returncode,'stdout':p.stdout,'stderr':p.stderr}
    (r/(name+'.upload.json')).write_text(json.dumps(receipt,indent=2)+'\n');receipts.append(receipt)
    assert p.returncode==0
    print(name,'uploaded',flush=True)
(r/'upload-receipts.json').write_text(json.dumps(receipts,indent=2)+'\n')
print('manifest_sha256',hashlib.sha256((r/'manifest.json').read_bytes()).hexdigest(),flush=True)
