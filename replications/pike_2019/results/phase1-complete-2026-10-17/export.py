import hashlib
import io
import json
import tarfile
from pathlib import Path

source = Path('/root/sugarscape/pike-remaining-001/phase1-195-300')
lines = (source / 'completed.jsonl').read_bytes().splitlines(keepends=True)
assert len(lines) == 105 and all(line.endswith(b'\n') for line in lines)
records = [json.loads(line) for line in lines]
assert all(record['exit_code'] == 0 for record in records)
manifest = json.loads((source / 'manifest.json').read_text())
output = Path('/root/sugarscape/pike-phase1-final-delta-001.tar.gz')
assert not output.exists()
with tarfile.open(output, 'w:gz') as archive:
    data = b''.join(lines[46:])
    info = tarfile.TarInfo('completed.jsonl')
    info.size = len(data)
    archive.addfile(info, io.BytesIO(data))
    for name in ['manifest.json', 'segment.json', *manifest['source_hashes']]:
        archive.add(source / name, arcname=name)
    for record in records[46:]:
        directory = Path(record['command'][-1])
        assert directory.parent == source
        archive.add(directory, arcname=directory.name)
        archive.add(source / f'{directory.name}.exit.json', arcname=f'{directory.name}.exit.json')
print(json.dumps({'sha256': hashlib.sha256(output.read_bytes()).hexdigest(),
                  'bytes': output.stat().st_size, 'ordinal_interval': [241, 300],
                  'conditions': 59, 'recorded_root': str(source)}))
