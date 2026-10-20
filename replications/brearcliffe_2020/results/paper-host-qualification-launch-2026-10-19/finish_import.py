"""Release only a verified input import, then preserve bounded qualification output."""
from pathlib import Path
import json
import subprocess
import time

root = Path(__file__).resolve().parent
node = 'relh-sugarscape-brearcliffe-paper-cpu8-20261019-v1'
deadline = time.monotonic() + 900
while True:
    state = json.loads(subprocess.check_output(['autor','api','get',f'/nodes/{node}/imports/imp-44ddq','--json']))
    (root / 'import-status.json').write_text(json.dumps(state,indent=2)+'\n')
    if state['status']=='complete':
        assert state['bytes_transferred']==32696568
        break
    assert state['status']=='running' and time.monotonic()<deadline
    time.sleep(10)
script="cd /root/sugarscape/brearcliffe-paper-host-qualification-001 && echo '184dffe53fbbde24d933715ec20722bb18cb1307970da60139f236793736cc36  staged-input/trial-input.tar.gz' | sha256sum -c - && touch input-ready"
p=subprocess.run(['autor','run',node,'--timeout','30','--json','--','sh','-c',script],capture_output=True,text=True)
(root/'input-ready.json').write_text(p.stdout)
assert p.returncode==0,p.stderr
assert json.loads(p.stdout)['exit_code']==0
collector=root.parent/'storage-handoff-20261017-001/collect_storage_api_bounded.py'
with (root/'collector.log').open('x') as log:
    p=subprocess.run(['/Users/relh/Code/workspace/sugarscape-replications/.venv/bin/python',str(collector),node,'cmd-922hc',root.name,'--terminal-file','/root/sugarscape/brearcliffe-paper-host-qualification-001/qualification-results.tar.gz','--seconds','7200','--max-bytes',str(50*1024**2)],stdout=log,stderr=subprocess.STDOUT,timeout=7400)
(root/'collection-terminal.json').write_text(json.dumps({'exit_code':p.returncode})+'\n')
assert p.returncode==0
