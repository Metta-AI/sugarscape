from pathlib import Path
import json,hashlib,tarfile
root=Path(__file__).resolve().parent
base=root.parent
prior=json.loads((base/'brearcliffe-ec-q-snapshot-001/union-audit/audit.json').read_text())
directories={r['run_id']:Path(r['directory']) for r in prior['completed']}
manifest={'archives': [entry for number in ('001', '002', '003') for entry in json.loads((base/f'brearcliffe-durable-evidence-{number}/manifest.json').read_text())['archives']]}
restored=[];verified=0
for entry in manifest['archives']:
    archive=Path(entry['local_source'])
    assert archive.stat().st_size==entry['bytes']
    assert hashlib.sha256(archive.read_bytes()).hexdigest()==entry['sha256']
    with tarfile.open(archive) as bundle:
        for member in bundle:
            if not member.isfile():
                assert member.isdir()
                continue
            data=bundle.extractfile(member).read()
            assert {'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}==entry['files'][member.name]
            parts=Path(member.name).parts
            ids=[(i,p) for i,p in enumerate(parts) if p in directories]
            if not ids:continue
            assert len(ids)==1
            i,run_id=ids[0]
            dest=directories[run_id].joinpath(*parts[i+1:])
            assert '..' not in parts
            if dest.exists():
                assert dest.read_bytes()==data
                verified+=1
            else:
                dest.parent.mkdir(parents=True,exist_ok=True)
                with dest.open('xb') as output:output.write(data)
                restored.append({'path':str(dest),'archive':entry['name'],'member':member.name,'sha256':hashlib.sha256(data).hexdigest()})
assert all((p/'provenance.json').is_file() for p in directories.values())
(root/'restoration.json').write_text(json.dumps({'restored_files':restored,'existing_files_verified':verified,'scope':'Restored missing files from retained hash-verified archives to their prior recorded paths. No existing files overwritten; no simulations rerun.'},indent=2)+'\n')
print('Restored',len(restored),'files; verified',verified,'existing files')
