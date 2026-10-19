import concurrent.futures,gzip,hashlib,json,subprocess,time
from pathlib import Path
root=Path(__file__).resolve().parent
prior=Path('/Users/relh/Code/workspace/sugarscape-stevenson/replications/stevenson_2021/results/birth-cost-ensemble-2026-10-15')
old={x['seed']:x for x in map(json.loads,(prior/'completed.jsonl').read_text().splitlines())}
protocol=dict(seeds=list(range(1,101)),infertility=10,birth_cost=40,cycles=150000,record_every=100,workers=2,seconds_per_run=120,windows=[[75000,100000],[130000,150000]],source_sha256=hashlib.sha256((root/'simulate.cpp').read_bytes()).hexdigest(),binary_sha256=hashlib.sha256((root/'simulate').read_bytes()).hexdigest(),runner_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),scope='Later-window sensitivity motivated by predecessor Figure14. Original target-paper window remains unknown. Same seeds and rules, all 100000-cycle prefixes must match before later metrics are analyzed. No replacement of primary ensemble or acceptance rule.')
(root/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n')

def execute(seed):
    trajectory=root/f'seed-{seed}.csv'
    observations=root/f'seed-{seed}-observations.csv'
    command=['/opt/homebrew/bin/gtimeout','--signal=TERM','--kill-after=10','120',str(root/'simulate'),str(seed),'10','40','150000','100',str(observations)]
    start=time.monotonic()
    with trajectory.open('w') as stdout,(root/f'seed-{seed}.stderr').open('w') as stderr:
        result=subprocess.run(command,stdout=stdout,stderr=stderr)
    record=dict(seed=seed,command=command,exit_code=result.returncode,elapsed_seconds=time.monotonic()-start,trajectory_sha256=hashlib.sha256(trajectory.read_bytes()).hexdigest(),observations_sha256=hashlib.sha256(observations.read_bytes()).hexdigest())
    (root/f'seed-{seed}-exit.json').write_text(json.dumps(record,indent=2)+'\n')
    assert result.returncode==0,record
    original=gzip.decompress((prior/f'seed-{seed}.csv.gz').read_bytes())
    assert hashlib.sha256(original).hexdigest()==old[seed]['trajectory_sha256']
    prefix=trajectory.read_bytes().splitlines(keepends=True)[:len(original.splitlines())]
    assert b''.join(prefix)==original,seed
    record['shared_prefix_observations']=len(prefix)-1
    return record

with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool,(root/'completed.jsonl').open('w') as ledger:
    for record in pool.map(execute,protocol['seeds']):
        ledger.write(json.dumps(record)+'\n');ledger.flush()
        print('Verified prefix, completed seed',record['seed'],flush=True)
(root/'terminal.json').write_text(json.dumps(dict(exit_code=0,completed_seeds=100))+'\n')
