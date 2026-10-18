from pathlib import Path
import hashlib
import json
import tarfile
root = Path(__file__).resolve().parent
output = root / 'source-readback'
output.mkdir()
records = []
for condition in json.loads((root / 'plan.json').read_text())['conditions']:
    size = condition['requested_cells']
    prefix = f'cells-{size}/'
    destination = output / f'cells-{size}'
    destination.mkdir()
    wanted = {'src/model/functions.c', 'run.log', 'build.log'}
    hashes = {}
    with tarfile.open(root / f'cells-{size}-evidence.tar.gz', 'r|gz') as archive:
        for member in archive:
            name = member.name.removeprefix(prefix)
            if member.isfile() and name in wanted:
                data = archive.extractfile(member).read()
                target = destination / name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(data)
                hashes[name] = hashlib.sha256(data).hexdigest()
    assert set(hashes) == wanted
    assert hashes['src/model/functions.c'] == condition['generated_model_sha256']
    assert (destination / 'src/model/functions.c').read_bytes() == (root / prefix / 'src/model/functions.c').read_bytes()
    assert 'Exit status: 0' in (destination / 'run.log').read_text()
    records.append({'requested_cells': size, 'files': hashes, 'generated_model_matches': True, 'native_exit_zero': True})
    print('Native source and exit verified', size, flush=True)
(output / 'audit.json').write_text(json.dumps(records, indent=2) + '\n')
