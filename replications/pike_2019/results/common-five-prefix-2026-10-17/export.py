from pathlib import Path
import json,tarfile,hashlib,io
source=Path('/root/sugarscape/pike-common-five-001');p=Path('/root/sugarscape/pike-common-five-prefix-001.tar.gz');assert not p.exists()
lines=(source/'completed.jsonl').read_bytes().splitlines(keepends=True)[:2];assert len(lines)>0 and all(x.endswith(b'\n') for x in lines)
manifest=json.loads((source/'manifest.json').read_text())
with tarfile.open(p,'w:gz') as t:
 data=b''.join(lines);info=tarfile.TarInfo('completed.jsonl');info.size=len(data);t.addfile(info,io.BytesIO(data))
 for name in ['manifest.json',*manifest['source_sha256']]:t.add(source/name,arcname=name)
 for line in lines:
  row=json.loads(line);assert row['exit_code']==0
  stem=f"{row['variant']}-{row['seed']}";t.add(source/stem,arcname=stem);t.add(source/(stem+'.exit.json'),arcname=stem+'.exit.json')
receipt={'conditions':len(lines),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
Path('/root/sugarscape/pike-common-five-prefix-001-export.json').write_text(json.dumps(receipt)+'\n');print(json.dumps(receipt))
