"""Select one original input per landscape/population stratum before timing runs."""
from pathlib import Path
import csv
import gzip
import hashlib
import io
import json
import random

root = Path(__file__).resolve().parent
source = root.parent / 'raimbault-generated-source-001/generated-raw.csv.gz'
rng = random.Random(20261016)
counts = {}
selected = {}
digest = hashlib.sha256()
with gzip.open(source, 'rb') as stream:
    while chunk := stream.read(1024*1024):
        digest.update(chunk)
assert digest.hexdigest() == '1a2cdf93167571ab2943d488017ace08945e7afd3cd8ac4d1410fb214c79c8f5'
with gzip.open(source, 'rt', newline='') as stream:
    reader = csv.DictReader(stream)
    fields = reader.fieldnames
    for index, row in enumerate(reader):
        key = (row['id'], float(row['population']))
        counts[key] = counts.setdefault(key, 0) + 1
        if rng.randrange(counts[key]) == 0:
            selected[key] = (index, row)
assert index + 1 == 2727994
assert len(selected) == 550
assert len({key[0] for key in selected}) == 50
assert {key[1] for key in selected} == set(range(10,511,50))
ordered = sorted(selected.values())
text = io.StringIO(newline='')
writer = csv.DictWriter(text, fieldnames=fields)
writer.writeheader()
writer.writerows(row for _, row in ordered)
with (root / 'selected.csv.gz').open('xb') as stream:
    stream.write(gzip.compress(text.getvalue().encode(),mtime=0))
report = {'original_sha256':digest.hexdigest(),'original_rows':2727994,'selected_rows':550,'selection':'One reservoir-sampled original input per landscape ID/population stratum. Selected before execution; use original stratum counts to weight runtime estimates.','random_seed':20261016,'selected_gzip_sha256':hashlib.sha256((root/'selected.csv.gz').read_bytes()).hexdigest(),'rows':[{'selected_row':i,'original_row':index,'id':row['id'],'population':float(row['population']),'seed':row['replication'],'stratum_rows':counts[(row['id'],float(row['population']))]} for i,(index,row) in enumerate(ordered)],'scope':'Throughput and fidelity sample only. No full generated-ensemble completion claim.'}
(root/'selection.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='rows'}))
