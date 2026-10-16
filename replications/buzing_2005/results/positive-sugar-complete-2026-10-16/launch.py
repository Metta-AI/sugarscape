from pathlib import Path
import json,subprocess,sys
out=Path(__file__).resolve().parent
protocol=json.loads((out/'protocol.json').read_text())
base=Path(protocol['baseline'])
completed=0
for model in protocol['conditions']['protocol']:
    for threshold in protocol['conditions']['threshold']:
        for seed in protocol['conditions']['seed']:
            name=f'{model}-ct{threshold}-seed{seed}'
            command=[sys.executable,str(out/'runner/audit_parent_fertility.py'),str(base/name),str(out/name),'own-range-positive-sugar']
            with (out/(name+'.log')).open('w') as log:
                p=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT)
            with (out/'completed.jsonl').open('a') as log:
                log.write(json.dumps({'name':name,'command':command,'exit_code':p.returncode})+'\n')
                log.flush()
            if p.returncode != 0:
                (out/'exit.json').write_text(json.dumps({'exit_code':p.returncode,'completed_runs':completed})+'\n')
                sys.exit(p.returncode)
            completed+=1
(out/'exit.json').write_text(json.dumps({'exit_code':0,'completed_runs':completed})+'\n')
