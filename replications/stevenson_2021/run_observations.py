"""Run the full declared elite/founder ensembles with exact prior-trajectory checks."""
import argparse
import csv
import gzip
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import time

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('binary',type=Path)
parser.add_argument('prior_low_fertility',type=Path)
parser.add_argument('prior_birth_cost',type=Path)
parser.add_argument('output',type=Path)
args=parser.parse_args()
binary=args.binary.resolve();root=Path(__file__).resolve().parent
args.output.mkdir(parents=True,exist_ok=False)
scenarios={'low-fertility':(85,0,args.prior_low_fertility),'birth-cost':(10,40,args.prior_birth_cost)}
manifest={'binary_sha256':hashlib.sha256(binary.read_bytes()).hexdigest(),
          'source_sha256':hashlib.sha256((root/'simulate.cpp').read_bytes()).hexdigest(),
          'protocol_sha256':hashlib.sha256((root/'OBSERVATION_PROTOCOL.md').read_bytes()).hexdigest(),
          'runner_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
          'cycles':50000,'record_every':100,'seeds':list(range(1,101)),
          'scope':'Additional observations of unchanged specification-based model; historical semantics remain unresolved.'}
(args.output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
(args.output/'OBSERVATION_PROTOCOL.md').write_bytes((root/'OBSERVATION_PROTOCOL.md').read_bytes())
with (args.output/'completed.jsonl').open('x') as ledger:
    for scenario,(infertility,cost,prior) in scenarios.items():
        previous={row['seed']:row for row in map(json.loads,(prior/'completed.jsonl').read_text().splitlines())}
        assert set(previous)==set(range(1,101))
        for seed in manifest['seeds']:
            assert shutil.disk_usage(args.output).free>=2*1024**3
            assert hashlib.sha256(binary.read_bytes()).hexdigest()==manifest['binary_sha256']
            old=(prior/f'seed-{seed}.csv').read_bytes()
            assert hashlib.sha256(old).hexdigest()==previous[seed]['trajectory_sha256']
            lines=old.splitlines(keepends=True)
            expected=lines[0]+b''.join(line for line in lines[1:] if int(line.split(b',')[0])<=50000)
            trajectory=args.output/f'{scenario}-{seed}.csv'
            observations=args.output/f'{scenario}-{seed}-observations.csv'
            command=[str(binary),str(seed),str(infertility),str(cost),'50000','100',str(observations.resolve())]
            started=time.monotonic()
            with trajectory.open('x') as stdout,trajectory.with_suffix('.stderr').open('x') as stderr:
                result=subprocess.run(command,stdout=stdout,stderr=stderr,check=False)
            (args.output/f'{scenario}-{seed}-exit.json').write_text(json.dumps({'exit_code':result.returncode})+'\n')
            assert result.returncode==0
            actual=trajectory.read_bytes();assert actual==expected,'Observation changed original trajectory'
            records=list(csv.DictReader(observations.open()))
            elite=[row for row in records if row['kind']=='elite']
            assert len(elite)==501
            assert [int(row['cycle']) for row in elite]==[1,*range(100,50001,100)]
            hashes={}
            for path in [trajectory,observations]:
                raw=path.read_bytes();compressed=gzip.compress(raw,mtime=0)
                assert gzip.decompress(compressed)==raw
                path.with_suffix(path.suffix+'.gz').write_bytes(compressed)
                hashes[path.name]=hashlib.sha256(raw).hexdigest()
            ledger.write(json.dumps({'scenario':scenario,'seed':seed,'command':command,'exit_code':0,
                                    'elapsed_seconds':time.monotonic()-started,'prior_prefix_byte_identical':True,
                                    'raw_sha256':hashes,'observation_rows':len(records)})+'\n');ledger.flush()
            print(f'Completed {scenario} seed {seed}',flush=True)
