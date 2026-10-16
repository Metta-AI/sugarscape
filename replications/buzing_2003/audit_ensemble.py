"""Audit the distinct 2003 grid and report descriptive outcomes without a paper verdict."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import statistics

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("ensemble", type=Path)
parser.add_argument("mode", choices=("prefix", "complete"))
parser.add_argument("output", type=Path)
args = parser.parse_args()
protocol = json.loads((args.ensemble / "protocol.json").read_text())
policies = ["none", "read", "response", "expiry-one"]
assert protocol["policies"] == policies and protocol["thresholds"] == list(range(5)) and protocol["seeds"] == list(range(10))
assert protocol["runs"] == 200 and protocol["cycles"] == 500
for name, checksum in protocol["runner_sha256"].items():
    assert hashlib.sha256((args.ensemble / "runner" / name).read_bytes()).hexdigest() == checksum
reference = Path(protocol["reference_run"])
assert hashlib.sha256((reference / "manifest.json").read_bytes()).hexdigest() == protocol["reference_manifest_sha256"]
ledger_bytes = (args.ensemble / "completed.jsonl").read_bytes()
ledger = [json.loads(line) for line in ledger_bytes.splitlines()]
expected = [f"{policy}-ct{ct}-seed{seed}" for policy in policies for ct in range(5) for seed in range(10)]
assert ledger and [r["name"] for r in ledger] == expected[:len(ledger)]
assert all(r["exit_code"] == 0 for r in ledger)
if args.mode == "complete":
    assert len(ledger) == 200
    assert json.loads((args.ensemble / "exit.json").read_text()) == {"exit_code": 0, "completed_runs": 200}
rows = []
trajectories = {}
for entry in ledger:
    path = args.ensemble / entry["name"]
    provenance = json.loads((path / "provenance.json").read_text())
    assert provenance["study"] == "Buzing2003" and provenance["cycles"] == 500
    policy, threshold, seed = provenance["policy"], provenance["threshold"], provenance["seed"]
    assert entry["name"] == f"{policy}-ct{threshold}-seed{seed}"
    assert provenance["reference_manifest"] == json.loads((reference / "manifest.json").read_text())
    for name, checksum in provenance["source_sha256"].items():
        assert hashlib.sha256(Path(name).read_bytes()).hexdigest() == checksum
    for name, checksum in provenance["configuration_sha256"].items():
        assert hashlib.sha256((path / name).read_bytes()).hexdigest() == checksum
    config = {}
    for name in ("Agent/agent.cfg", "Scape/scape.cfg", "Experiment/experiment.cfg"):
        config[name] = {line.split('=', 1)[0].strip(): line.split('=', 1)[1].strip()
                        for line in (path / 'config' / name).read_text().splitlines()
                        if '=' in line and not line.lstrip().startswith('#')}
    numeric = {
        "Agent/agent.cfg": {"minVision": 1, "maxVision": 1, "minSugarMetabolism": 1, "maxSugarMetabolism": 1,
            "minInitialSugar": 50, "maxInitialSugar": 50, "minReproductionSugar": 5, "maxReproductionSugar": 5,
            "minDeathAge": 60, "maxDeathAge": 100, "minBeginChildBearingAge": 12, "maxBeginChildBearingAge": 15,
            "minEndChildBearingAgeMales": 50, "maxEndChildBearingAgeMales": 60,
            "minEndChildBearingAgeFemales": 40, "maxEndChildBearingAgeFemales": 50, "sexRecoveryPeriod": 0,
            "mutationSigma": .01, "minListenPref": int(policy != "none"), "maxListenPref": int(policy != "none"),
            "minTalkPref": 0, "maxTalkPref": int(policy != "none"), "maxSugarHarvest": threshold},
        "Scape/scape.cfg": {"width": 50, "height": 50, "initialPopulation": 400, "sugarRichness": .5,
            "sugarGrowBackRate": 3, "randomSeed": seed, "message.removeAfterNIterations": int(policy == "expiry-one")},
        "Experiment/experiment.cfg": {"runLength": 500, "numberOfRuns": 1, "nrOfSubcycles": 1},
    }
    for name, values in numeric.items():
        for key, value in values.items():
            assert float(config[name][key].removesuffix('f')) == value, (name, key)
    for name, values in {
        "Agent/agent.cfg": {"mutationOperator.listenPref": False, "mutationOperator.talkPref": policy != "none", "initAgeZero": False, "preferNearestCell": False, "replacement": False, "allowSex": True},
        "Scape/scape.cfg": {"message.removeAfterListening": policy == "read", "message.removeAfterResponse": policy == "response", "reseedSugar": True},
    }.items():
        for key, value in values.items():
            assert config[name][key] == str(value).lower()
    assert json.loads((path / "exit.json").read_text()) == {"exit_code": 0}
    audit = json.loads((path / "audit.json").read_text())
    series = {}
    for name, checksum in audit["output_sha256"].items():
        raw = (path / "data" / name).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == checksum
        if name.endswith('.avg'):
            values = [line.split() for line in raw.decode().splitlines()]
            assert [int(r[0]) for r in values] == list(range(500))
            assert all(len(r) == 2 and math.isfinite(float(r[1])) for r in values)
            series[name] = [float(r[1]) for r in values]
    assert len(series) == 7
    population = series['experiment_0_.numberOfAgents.avg']
    assert all(n.is_integer() and n >= 0 for n in population)
    extinct = next((i for i, n in enumerate(population) if n == 0), None)
    if extinct is not None:
        assert all(n == 0 for n in population[extinct:])
    assert all(v == int(policy != 'none') for v, n in zip(series['experiment_0_.listenPref.avg'], population) if n > 0)
    talk = series['experiment_0_.talkPref.avg']
    assert all(0 <= v <= 1 for v in talk)
    if policy == 'none':
        assert all(v == 0 for v in talk)
    log_bytes = (path / 'run.log').read_bytes()
    log = log_bytes.decode()
    assert f'iterations=500,initial=400,final={int(population[-1])}' in log
    births = [list(map(float, line.split(',')[1:])) for line in log.splitlines() if line.startswith('birth2003,')]
    assert len(births) == audit['births'] and all(0 <= r[0] < 500 and r[1] > 5 and r[2] > 5 for r in births)
    counts = [list(map(int, line.split(',')[1:])) for line in log.splitlines() if line.startswith('harvest-counts,')]
    assert [r[0] for r in counts] == list(range(500))
    assert all(0 <= shared <= meals <= consumers and 2 * shared <= shared_consumers <= consumers
               and meals - shared == consumers - shared_consumers for _, meals, shared, consumers, shared_consumers in counts)
    late_counts = [sum(r[j] for r in counts[250:]) for j in range(1, 5)]
    alive = [i for i in range(250, 500) if population[i] > 0]
    rows.append({'name': entry['name'], 'policy': policy, 'threshold': threshold, 'seed': seed,
                 'final_population': population[-1], 'extinction_cycle': extinct + 1 if extinct is not None else None,
                 'late_population_mean': statistics.mean(population[250:]), 'late_population_temporal_sd': statistics.pstdev(population[250:]),
                 'late_talk_alive_mean': statistics.mean(talk[i] for i in alive) if alive else None,
                 'late_native_cooperation_alive_mean': statistics.mean(series['experiment_0_.cooperating.avg'][i] for i in alive) if alive else None,
                 'late_shared_event_fraction': late_counts[1] / late_counts[0] if late_counts[0] else None,
                 'late_shared_participant_fraction': late_counts[3] / late_counts[2] if late_counts[2] else None,
                 'births': len(births), 'log_sha256': hashlib.sha256(log_bytes).hexdigest(), 'output_sha256': audit['output_sha256']})
    trajectories[entry['name']] = population
groups = []
for policy in policies:
    for threshold in range(5):
        members = [r for r in rows if r['policy'] == policy and r['threshold'] == threshold]
        if not members:
            continue
        groups.append({'policy': policy, 'threshold': threshold, 'seeds': len(members),
                       'surviving_seeds': sum(r['final_population'] > 0 for r in members),
                       'late_population_mean': statistics.mean(r['late_population_mean'] for r in members),
                       'mean_temporal_sd': statistics.mean(r['late_population_temporal_sd'] for r in members),
                       'mean_cross_seed_sd_by_cycle': None if len(members) == 1 else
                           statistics.mean(statistics.pstdev(trajectories[r['name']][i] for r in members) for i in range(250, 500))})
report = {'mode': args.mode, 'complete': args.mode == 'complete', 'runs': len(rows), 'scalar_observations': len(rows) * 3500,
          'births': sum(r['births'] for r in rows), 'ledger_sha256': hashlib.sha256(ledger_bytes).hexdigest(),
          'groups': groups, 'run_results': rows,
          'measurement': 'Late window cycles251–500 is descriptive. Population zeros retained after extinction; gene and agent-cooperation means omit empty populations. Event and participant ratios remain distinct.',
          'scope': 'Policy-uncertain reconstruction. Neither an automatic paper verdict nor selection of a historically correct policy.'}
args.output.mkdir(parents=True, exist_ok=False)
(args.output / 'audit.json').write_text(json.dumps(report, indent=2, allow_nan=False) + '\n')
print(json.dumps({k: v for k, v in report.items() if k not in ('groups', 'run_results')}))
