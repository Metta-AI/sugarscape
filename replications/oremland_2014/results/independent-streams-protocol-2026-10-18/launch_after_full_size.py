from pathlib import Path
import json,os,subprocess,time
root=Path(__file__).parent
previous=root.with_name('oremland-full-size-rankings-001')/'execution'
manifest={'launcher_pid':json.loads((previous.parent/'queued-launch.json').read_text())['pid']}
command=['/Users/relh/Code/workspace/sugarscape-replications/.venv/bin/python','/Users/relh/Code/workspace/sugarscape-oremland/replications/oremland_2014/run_rankings.py','/opt/homebrew/opt/openjdk@11','/Users/relh/Code/workspace/sugarscape-replication-tools/netlogo-5.3.1-64/app',str(root),'--timeout','/opt/homebrew/bin/gtimeout','--gzip','/usr/bin/gzip']
with (root/'queued-launch.json').open('x') as stream:
 stream.write(json.dumps({'pid':os.getpid(),'waiting_for_launcher_pid':manifest['launcher_pid'],'waiting_for_exit':str(previous/'exit.json'),'command':command,'maximum_wait_seconds':7400,'started_unix':time.time()},indent=2)+'\n')
deadline=time.monotonic()+7400
while not (previous/'exit.json').exists() and time.monotonic()<deadline:
 os.kill(manifest['launcher_pid'],0)
 time.sleep(5)
assert (previous/'exit.json').exists(), 'Existing batch lacks terminal evidence; do not duplicate it.'
subprocess.run(command,check=True)
