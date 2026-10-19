from pathlib import Path
import difflib
import hashlib
import json
import tarfile

root = Path(__file__).resolve().parent
receipts = json.loads((root / 'receipts.json').read_text())
files = {}
for version, receipt in receipts.items():
    archive = root / f'abctools_{version}.tar.gz'
    assert archive.stat().st_size == receipt['bytes']
    assert hashlib.sha256(archive.read_bytes()).hexdigest() == receipt['sha256']
    with tarfile.open(archive) as tar:
        files[version] = {m.name: tar.extractfile(m).read() for m in tar.getmembers()
                          if m.isfile() and m.name.startswith('abctools/R/')}
name = 'abctools/R/semiauto.abc.R'
old = files['1.1.3'][name]
new = files['1.1.8'][name]
assert old.count(b'if(class(te)=="try-error")') == 1
assert old.replace(b'if(class(te)=="try-error")', b'if(is(te,"try-error"))') == new
(root / 'semiauto.diff').write_text(''.join(difflib.unified_diff(
    old.decode().splitlines(keepends=True), new.decode().splitlines(keepends=True),
    fromfile='abctools-1.1.3/semiauto.abc.R', tofile='abctools-1.1.8/semiauto.abc.R')))
result = {
    'archives': receipts,
    'semiauto_sha256': {v: hashlib.sha256(f[name]).hexdigest() for v, f in files.items()},
    'semiauto_only_change': 'if(class(te)=="try-error") becomes if(is(te,"try-error")) in transformation validation',
    'sampling_and_regression_source_unchanged': True,
    'changed_common_R_files': [n for n in sorted(files['1.1.3'].keys() & files['1.1.8'].keys())
                             if files['1.1.3'][n] != files['1.1.8'][n]],
    'removed_R_files': sorted(files['1.1.3'].keys() - files['1.1.8'].keys()),
    'added_R_files': sorted(files['1.1.8'].keys() - files['1.1.3'].keys()),
    'scope': 'Source comparison only. Does not establish identical historical dependencies, RNG, runtime, or published results.'
}
(root / 'comparison.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
