import hashlib
import json
import tarfile
from pathlib import Path

root = Path('/root/sugarscape/pike-remaining-001')
snapshot = Path('/root/sugarscape/pike-checkpoint-002')
snapshot.mkdir()
segments = []
with tarfile.open('/root/sugarscape/pike-checkpoint-002.tar.gz', 'w:gz') as archive:
    for name in ['plan.json', 'run.py', 'run.sh']:
        archive.add(root/name, arcname=name)
    for source in sorted(root.glob('phase*-*-*')):
        if not source.is_dir() or source.name.startswith('phase1-'):
            continue
        ledger = (source/'completed.jsonl').read_bytes()
        lines = ledger.splitlines(keepends=True)
        if lines and not lines[-1].endswith(b'\n'):
            lines.pop()
        records = [json.loads(line) for line in lines]
        if not records:
            continue
        phase, start, stop = map(int, source.name.replace('phase', '').split('-'))
        target = snapshot/source.name
        target.mkdir()
        (target/'completed.jsonl').write_bytes(b''.join(lines))
        archive.add(target/'completed.jsonl', arcname=f'{source.name}/completed.jsonl')
        manifest = json.loads((source/'manifest.json').read_text())
        key = 'source_hashes' if phase == 1 else 'source_sha256'
        for name in ['manifest.json','segment.json',*manifest[key]]:
            archive.add(source/name,arcname=f'{source.name}/{name}')
        for record in records:
            directory = Path(record['command'][-1])
            assert directory.parent == source and record['exit_code'] == 0
            archive.add(directory, arcname=f'{source.name}/{directory.name}')
            archive.add(source/f'{directory.name}.exit.json',arcname=f'{source.name}/{directory.name}.exit.json')
        segments.append({'phase':phase,'start':start,'completed':len(records),'recorded_root':str(source),'snapshot':source.name})
    report={'segments':segments,'completed':sum(s['completed'] for s in segments),'scope':'Completed ledger entries only; active partial conditions excluded.'}
    (snapshot/'checkpoint.json').write_text(json.dumps(report,indent=2)+'\n')
    archive.add(snapshot/'checkpoint.json',arcname='checkpoint.json')
p=Path('/root/sugarscape/pike-checkpoint-002.tar.gz')
print(json.dumps({'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size,**report}))
