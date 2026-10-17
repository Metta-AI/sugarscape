import hashlib,io,json,tarfile
from pathlib import Path
root=Path('/root/sugarscape/pike-remaining-001')
output=Path('/root/sugarscape/pike-phase2-final-delta-002.tar.gz')
assert not output.exists()
intervals=[]
with tarfile.open(output,'w:gz') as archive:
 for name,start,offset in [('phase2-62-331',62,212),('phase2-331-600',331,209)]:
  source=root/name
  lines=(source/'completed.jsonl').read_bytes().splitlines(keepends=True)
  assert len(lines)==269 and all(line.endswith(b'\n') for line in lines)
  records=[json.loads(line) for line in lines]
  assert all(record['exit_code']==0 for record in records)
  manifest=json.loads((source/'manifest.json').read_text())
  data=b''.join(lines[offset:]);info=tarfile.TarInfo(name+'/completed.jsonl');info.size=len(data);archive.addfile(info,io.BytesIO(data))
  for filename in ['manifest.json','segment.json',*manifest['source_sha256']]:archive.add(source/filename,arcname=name+'/'+filename)
  for record in records[offset:]:
   directory=Path(record['command'][-1]);assert directory.parent==source
   archive.add(directory,arcname=name+'/'+directory.name)
   archive.add(source/(directory.name+'.exit.json'),arcname=name+'/'+directory.name+'.exit.json')
  intervals.append([start+offset,start+len(lines)])
receipt={'sha256':hashlib.sha256(output.read_bytes()).hexdigest(),'bytes':output.stat().st_size,'intervals':intervals}
Path('/root/sugarscape/pike-phase2-final-delta-002.json').write_text(json.dumps(receipt)+'\n')
print(json.dumps(receipt))
