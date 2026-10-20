"""Run the unmodified pension model through native BehaviorSpace, bounded per process."""
import csv
import hashlib
import json
from pathlib import Path
import subprocess
import time
import xml.etree.ElementTree as ET

root = Path(__file__).resolve().parent
source = root.parent / 'pensions-source-001/Sugarscape Pension Law.nlogo'
runtime = root.parent.parent / 'sugarscape-replication-tools/netlogo-6.1.0-runtime-001/NetLogo 6.1.0'
assert hashlib.sha256(source.read_bytes()).hexdigest() == '3cd89b39a9bfdd30adb84b6ed6056215097a26bfd9eaa39dc524e8dedb6fc27d'
text = source.read_text()
experiments = text[text.index('<experiments>'):text.index('</experiments>') + len('</experiments>')]
protocol = {'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(), 'runtime_jars': {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((runtime/'app').glob('*.jar'))}, 'seed_base': 20261018, 'steps':1000, 'condition': {}, 'cases':['full-grid'], 'seconds_per_case':7200, 'scope':'Full 128 conditions with ten repetitions each, original 1000-step horizon. Explicit seeds 20261018 + BehaviorSpace run number; no historical seed or paper-level agreement claim.', 'runner_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
(root/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n')
for case in protocol['cases']:
    folder=root/case;folder.mkdir()
    exp=next(x for x in ET.fromstring(experiments) if x.attrib['name']=='pensionsExperiments')
    assert exp.attrib['repetitions']=='10';exp.set('runMetricsEveryStep',str(case=='dense').lower())
    exp.find('setup').text='random-seed (20261018 + behaviorspace-run-number) setup'
    for values in exp.findall('enumeratedValueSet'):
        variable=values.attrib['variable']
        if variable in protocol['condition']:
            for value in list(values):values.remove(value)
            ET.SubElement(values,'value',value=protocol['condition'][variable])
    ET.SubElement(exp,'metric').text='20261018 + behaviorspace-run-number'
    ET.SubElement(exp,'metric').text='count turtles'
    for metric in list(exp.findall('metric'))[-2:]:
        exp.remove(metric)
        exp.insert(list(exp).index(exp.find('enumeratedValueSet')), metric)
    doc=ET.Element('experiments');doc.append(exp)
    ET.ElementTree(doc).write(folder/'experiment.xml',encoding='utf-8',xml_declaration=False)
    command=['/opt/homebrew/opt/openjdk@11/bin/java','-Xmx512m','-XX:ActiveProcessorCount=1','-Djava.awt.headless=true','-Dfile.encoding=UTF-8','-cp',str(runtime/'app/*'),'org.nlogo.headless.Main','--model',str(source),'--setup-file',str(folder/'experiment.xml'),'--experiment','pensionsExperiments','--threads','1','--table',str(folder/'trajectory.csv')]
    (folder/'command.json').write_text(json.dumps(command,indent=2)+'\n')
    start=time.monotonic()
    with (folder/'stdout.log').open('x') as out,(folder/'stderr.log').open('x') as err:
        result=subprocess.run(command,cwd=runtime,stdout=out,stderr=err,timeout=7200)
    (folder/'exit.json').write_text(json.dumps({'exit_code':result.returncode,'elapsed_seconds':time.monotonic()-start})+'\n');result.check_returncode()
    print(case,'completed',flush=True)
assert hashlib.sha256(source.read_bytes()).hexdigest()==protocol['source_sha256']
(root/'completed.json').write_text(json.dumps({'files_sha256':{str(f.relative_to(root)):hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(root.glob('*/*')) if f.is_file()}} ,indent=2)+'\n')
