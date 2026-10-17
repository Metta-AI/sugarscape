"""Collect the declared complete intervals, preserving interrupted attempts separately."""
import argparse
import csv
import hashlib
import json
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('evidence',type=Path)
parser.add_argument('output',type=Path)
args=parser.parse_args()
assert not args.output.exists()
intervals=[
 ('carrella-2021-ensemble-0-001',0,256),
 ('carrella-2021-resumed-256-001',256,1250),
 ('carrella-2021-ensemble-1250-001',1250,1516),
 ('carrella-2021-resumed-1516-001',1516,2500),
 ('carrella-2021-ensemble-2500-001',2500,2768),
 ('carrella-2021-resumed-2768-001',2768,3111),
 ('carrella-2021-resumed-3111-001',3111,3750),
 ('carrella-2021-ensemble-3750-001',3750,4016),
 ('carrella-2021-resumed-4016-001',4016,5000),
]
records=[]
for directory,start,stop in intervals:
    for index in range(start,stop):
        path=(args.evidence/directory/f'row-{index}.csv').resolve()
        with path.open() as stream:
            rows=list(csv.reader(stream))
        assert len(rows)==502 and all(len(row)==7 for row in rows),path
        records.append({'row':index,'source':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
assert [r['row'] for r in records]==list(range(5000))
args.output.mkdir(parents=True)
(args.output/'trajectories').mkdir()
for record in records:
    (args.output/'trajectories'/f"row-{record['row']}.csv").symlink_to(record['source'])
(args.output/'assembly.json').write_text(json.dumps({'intervals':intervals,'rows':records,'note':'Interrupted truncated outputs are retained at their original paths. The extinction-stopped row3110 is complete and was independently validated; replacement intervals were declared from verified last complete inputs.'},indent=2)+'\n')
print('Assembled 5000 complete 501-observation trajectories; statistical comparison still required.')
