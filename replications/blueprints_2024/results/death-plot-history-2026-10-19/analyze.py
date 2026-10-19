from pathlib import Path
import ast,csv,json,hashlib,tarfile,statistics
r=Path(__file__).resolve().parent;repo=Path('/Users/relh/Code/workspace/sugarscape-blueprints');source=repo/'replications/blueprints_2024/results/heterogeneous50-complete-2026-10-19/population';summary=json.loads((source/'summary.json').read_text());expected={x['trajectory_sha256']:x for x in csv.DictReader((source/'per-run.csv').open())};assert len(expected)==500
columns=['population','agentWealthTotal','agentStarvationDeaths','agentCombatDeaths','agentAgingDeaths','agentDiseaseDeaths'];metrics={k:[0.0]*5001 for k in columns};seen=set()
for name,pin in summary['native_archive_sha256'].items():
 p=repo/name;assert hashlib.sha256(p.read_bytes()).hexdigest()==pin
 with tarfile.open(p,'r|gz') as tar:
  for member in tar:
   if not member.name.endswith('/trajectory.json'):continue
   raw=tar.extractfile(member).read();sha=hashlib.sha256(raw).hexdigest()
   if sha not in expected:continue
   assert sha not in seen;seen.add(sha);rows=json.loads(raw);assert len(rows)==int(expected[sha]['observations'])
   for t,row in enumerate(rows):
    assert row['timestep']==t
    for k in columns:metrics[k][t]+=row[k]
assert seen==expected.keys()
p=r/'cc0408a-plot.py';pins=json.loads((r/'source-pins.json').read_text());pin=next(x for x in pins if x['file']==p.name);assert hashlib.sha256(p.read_bytes()).hexdigest()==pin['sha256']
tree=ast.parse(p.read_text());function=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='findMeans');module=ast.Module(body=[function],type_ignores=[]);namespace={'totalTimesteps':5000,'datacols':columns};exec(compile(module,str(p),'exec'),namespace)
dataset={'heterogeneous50':{'runs':500,'metrics':metrics,'means':{}}};result=namespace['findMeans'](dataset)['heterogeneous50']['means'];rates=result['meanDeaths'];assert len(rates)==5001
with (r/'per-timestep.csv').open('w') as f:
 w=csv.writer(f);w.writerow(['timestep',*columns,'author_meanDeaths_percent']);w.writerows([t,*[metrics[k][t] for k in columns],rates[t]] for t in range(5001))
report={'inputs':500,'executed_source_commit':pin['commit'],'executed_function':'findMeans','method':'Unmodified function extracted with AST; actual500-run per-timestep sums, zero initialized after extinction as author parseDataset does.','source_author_formula':'100*(sum starvation+sum combat+sum aging)/sum population per timestep, zero if denominator0','death_rate_percent':{'mean_including_initial':statistics.mean(rates),'mean_excluding_initial':statistics.mean(rates[1:]),'median_including_initial':statistics.median(rates),'median_excluding_initial':statistics.median(rates[1:])},'disease_deaths_total':sum(metrics['agentDiseaseDeaths']),'scope':'Later author plotting function executed on pinned2024.1 trajectories. It plots a homogeneous ensemble time series, not demonstrated historical Figure20 calculation. Temporal mean and median are diagnostic summaries, not new acceptance criteria.'};(r/'summary.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
