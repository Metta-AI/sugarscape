from pathlib import Path
import concurrent.futures
import hashlib
import json
import subprocess
import tarfile

root = Path(__file__).resolve().parent
base = root.parent
archive = root/'checkpoint.tar.gz'
expected = json.loads((root/'export.json').read_text())
assert hashlib.sha256(archive.read_bytes()).hexdigest() == expected['sha256']
download = root/'download'
download.mkdir()
with tarfile.open(archive) as bundle:
    bundle.extractall(download,filter='data')
checkpoint=json.loads((download/'checkpoint.json').read_text())
assert checkpoint['completed']==expected['completed']==158
python=base.parent/'sugarscape-replications/.venv/bin/python'
script=base.parent/'sugarscape-pike/replications/pike_2019/reconcile_segments.py'
commands=[]
for phase,original,old_count in [(1,'pike-phase1-001',194),(2,'pike-phase2-001',61),(3,'pike-phase3-movement-001',29)]:
    original=base/original
    new=base/f'pike-segment-phase{phase}-003'
    command=[str(python),str(script),str(phase),str(root/f'reconciled-phase{phase}'),'--segment',str(original),'0',str(original),'--segment',str(new),str(old_count),str(new)]
    for segment in checkpoint['segments']:
        if segment['phase']==phase:
            command.extend(['--segment',str(download/segment['snapshot']),str(segment['start']),segment['recorded_root']])
    commands.append(command)
(root/'commands.json').write_text(json.dumps(commands,indent=2)+'\n')
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
    results=list(pool.map(lambda command:subprocess.run(command,capture_output=True,text=True),commands))
for phase,result in enumerate(results,1):
    (root/f'phase{phase}.log').write_text(result.stdout+result.stderr)
    assert result.returncode==0,(phase,result.stderr)
reports=[json.loads((root/f'reconciled-phase{phase}/reconciliation.json').read_text()) for phase in range(1,4)]
summary={'archive_sha256':expected['sha256'],'new_cloud_conditions':158,'total_conditions':sum(r['validated_runs'] for r in reports),'phase_counts':[r['validated_runs'] for r in reports],'health_records':sum(r['health_records'] for r in reports),'price_step_records':sum(r['price_step_records'] for r in reports),'scope':'Original local terminal prefixes plus three local continuations plus disjoint cloud snapshot. Portability duplicates excluded. All grids remain incomplete.'}
assert summary['total_conditions']==287+158
(root/'validation.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary))
