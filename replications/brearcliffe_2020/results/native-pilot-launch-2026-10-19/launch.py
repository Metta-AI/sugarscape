from pathlib import Path
import subprocess,time,json,shutil
r=Path(__file__).resolve().parent
assert shutil.disk_usage(r).free>2*1024**3
command=['/opt/homebrew/opt/openjdk@11/bin/java','-Xmx1g','-Djava.awt.headless=true','-cp',str(r)+':/Users/relh/Code/workspace/sugarscape-replication-tools/NetLogo 6.1.1/app/*','Replay',str(r/'model.nlogo'),'Rule M','EC','20000',str(r/'trajectory.csv')]
(r/'command.json').write_text(json.dumps(command,indent=2)+'\n')
start=time.monotonic()
with (r/'terminal.log').open('x') as log:
    result=subprocess.run(command,cwd=r,stdout=log,stderr=subprocess.STDOUT,timeout=600)
receipt={'exit_code':result.returncode,'elapsed_seconds':time.monotonic()-start,'output_bytes':sum(p.stat().st_size for p in r.rglob('*') if p.is_file())}
(r/'terminal.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt))
assert result.returncode==0
assert receipt['output_bytes']<52428800
