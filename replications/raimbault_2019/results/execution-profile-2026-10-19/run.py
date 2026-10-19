from pathlib import Path
import hashlib
import json
import subprocess
import time

root = Path(__file__).resolve().parent
source = root.parent / 'raimbault-gini-qualification-001'
app = Path('/Users/relh/Code/workspace/sugarscape-replication-tools/netlogo-5.3.1-64/app')
java = Path('/opt/homebrew/opt/openjdk@11/bin/java')
files = [source / 'GiniReplay.java', source / 'selected.csv.gz', *sorted((source / 'baseline').rglob('*')), *sorted(app.glob('*.jar'))]
pins = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in files if p.is_file()}
cmd = [str(java), '-Djava.awt.headless=true', '-Xmx768m', '-XX:FlightRecorderOptions=stackdepth=128',
       '-XX:StartFlightRecording=filename=' + str(root / 'execution.jfr') + ',settings=profile,dumponexit=true,maxsize=64m',
       '-cp', str(app / 'NetLogo.jar') + ':' + str(app / '*'), str(source / 'GiniReplay.java'),
       str(source / 'baseline/HEADLESS_Sugarscape.nlogo'), str(source / 'selected.csv.gz'), '0', '2', str(root / 'results.csv')]
(root / 'protocol.json').write_text(json.dumps({'command': cmd, 'timeout_seconds': 120, 'recording_max_bytes': 64 * 1024**2,
    'source_sha256': pins, 'scope': 'Profile the unchanged qualified model at populations10/510 through10000 ticks. Instrumented time is not a speed benchmark; exact histories and worlds must match prior baseline before interpreting samples.'}, indent=2) + '\n')
started = time.monotonic()
with (root / 'run.log').open('x') as log:
    result = subprocess.run(cmd, cwd=source / 'baseline', stdout=log, stderr=subprocess.STDOUT, timeout=120)
(root / 'terminal.json').write_text(json.dumps({'exit_code': result.returncode, 'elapsed_seconds': time.monotonic()-started}, indent=2)+'\n')
assert result.returncode == 0
with (root / 'samples.json').open('x') as out:
    subprocess.run([str(java.parent / 'jfr'), 'print', '--json', '--events', 'jdk.ExecutionSample', '--stack-depth', '128', str(root / 'execution.jfr')], stdout=out, check=True, timeout=60)
print('Profile run and sample extraction complete', flush=True)
