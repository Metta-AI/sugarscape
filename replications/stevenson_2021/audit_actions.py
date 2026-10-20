"""Replay complete action tapes independently; require unchanged native outputs."""
import argparse
import csv
import gzip
import hashlib
import json
from pathlib import Path
import subprocess


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('output', type=Path)
args = parser.parse_args()
root = args.output
root.mkdir()
source = Path(__file__).with_name('simulate.cpp').read_text()
assert hashlib.sha256(source.encode()).hexdigest() == '17803df8b61cfded16718e4895cf574cae77aa514e57a79f99413d7173d49fbc'
replacements = [
    ('    occupied[initial] = true;', '''    occupied[initial] = true;
    std::ofstream tape(std::string(argv[6]) + ".tape");
    tape.exceptions(std::ios::failbit | std::ios::badbit);
    tape << "I," << initial << '\\n';
    auto trace = [&](int cycle, std::size_t index, int draw, std::size_t birth_index) {
        const auto& a = agents[index];
        tape << "A," << cycle << ',' << a.id << ',' << a.cell << ',' << a.wealth
             << ',' << a.age << ',' << a.alive << ',' << draw << ','
             << (agents.size() > birth_index ? agents.back().cell : -1) << '\\n';
    };'''),
    ('            ++agent.age;', '''            ++agent.age;
            const auto birth_index = agents.size();
            int fertility_draw = 0;'''),
    ('                ++deaths;\n                continue;', '''                ++deaths;
                trace(cycle, index, fertility_draw, birth_index);
                continue;'''),
    ('''            if (agent.age >= 1 && agent.wealth >= birth_cost &&
                std::uniform_int_distribution<int>(1, infertility)(random) == 1) {''',
     '''            if (agent.age >= 1 && agent.wealth >= birth_cost)
                fertility_draw = std::uniform_int_distribution<int>(1, infertility)(random);
            if (fertility_draw == 1) {'''),
    ('        }\n        agents.erase(', '            trace(cycle, index, fertility_draw, birth_index);\n        }\n        agents.erase('),
    ('        const auto landscape =', '        tape << "E," << cycle << \'\\n\';\n        const auto landscape ='),
]
observed = source
for old, new in replacements:
    assert observed.count(old) == 1
    observed = observed.replace(old, new)
(root / 'baseline.cpp').write_text(source)
(root / 'observed.cpp').write_text(observed)
compiler = subprocess.check_output(['clang++', '--version'], text=True)
for variant in ['baseline', 'observed']:
    subprocess.run(['clang++', '-std=c++17', '-O2', '-Wall', '-Wextra', '-Werror',
                    str(root / f'{variant}.cpp'), '-o', str(root / variant)], check=True, timeout=60)
protocol = {
    'seed': 20261020, 'cycles': 2000, 'record_every': 1,
    'scenarios': {'low-fertility': [85, 0], 'birth-cost': [10, 40], 'dense-control': [10, 0]},
    'compiler': compiler,
    'source_sha256': hashlib.sha256(source.encode()).hexdigest(),
    'scope': 'Implementation validation conditional on documented rules; not historical-author-code identity or a paper replication verdict.',
    'unverified': ['RNG distribution and historical seed identity', 'undocumented author rule choices', 'evolutionary extension'],
}
(root / 'protocol.json').write_text(json.dumps(protocol, indent=2) + '\n')
reports = []
for scenario, (infertility, cost) in protocol['scenarios'].items():
    for variant in ['baseline', 'observed']:
        stem = root / f'{scenario}-{variant}'
        with stem.with_suffix('.csv').open('x') as out, stem.with_suffix('.stderr').open('x') as err:
            subprocess.run([str(root / variant), str(protocol['seed']), str(infertility), str(cost),
                            str(protocol['cycles']), '1', str(stem.with_suffix('.observations'))],
                           stdout=out, stderr=err, check=True, timeout=180)
        assert stem.with_suffix('.stderr').read_bytes() == b''
    for suffix in ['.csv', '.observations']:
        assert (root / f'{scenario}-baseline{suffix}').read_bytes() == (root / f'{scenario}-observed{suffix}').read_bytes()

    # Independent Python state; no C++ visibility table or aggregate arithmetic is imported.
    landscape = [4] * 2500
    agents = {}
    occupied = set()
    expected = set()
    cycle = 1
    next_id = 1
    births = deaths = actions = 0
    total_births = total_deaths = 0
    with (root / f'{scenario}-baseline.csv').open() as aggregate, (root / f'{scenario}-observed.observations.tape').open() as tape:
        metrics = csv.DictReader(aggregate)
        for raw in tape:
            kind, *values = raw.strip().split(',')
            numbers = list(map(int, values))
            if kind == 'I':
                assert not agents and cycle == 1
                cell, = numbers
                assert 0 <= cell < 2500
                agents[0] = (cell, 0, 0)
                occupied.add(cell)
                expected = {0}
            elif kind == 'A':
                t, identity, target, wealth, age, alive, draw, newborn = numbers
                assert t == cycle and identity in expected
                expected.remove(identity)
                cell, old_wealth, old_age = agents[identity]
                x, y = cell % 50, cell // 50
                choices = {cell: 0}
                for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                    for distance in range(1, 7):
                        candidate = ((y + dy * distance) % 50) * 50 + (x + dx * distance) % 50
                        if candidate not in occupied:
                            choices[candidate] = distance
                best = max((landscape[c], -d) for c, d in choices.items())
                assert target in choices and (landscape[target], -choices[target]) == best
                occupied.remove(cell)
                occupied.add(target)
                available = old_wealth + landscape[target]
                landscape[target] = 0
                assert age == old_age + 1 and alive == int(available >= 3)
                if not alive:
                    assert wealth == available and draw == 0 and newborn == -1
                    occupied.remove(target)
                    del agents[identity]
                    deaths += 1
                else:
                    available -= 3
                    if available >= cost:
                        assert 1 <= draw <= infertility
                    else:
                        assert draw == 0
                    tx, ty = target % 50, target // 50
                    neighbors = {((ty + dy) % 50) * 50 + (tx + dx) % 50
                                 for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]}
                    empty = neighbors - occupied
                    reproduces = draw == 1 and bool(empty)
                    assert (newborn != -1) == reproduces
                    if reproduces:
                        assert newborn in empty
                        available -= cost
                        agents[next_id] = (newborn, 0, 0)
                        occupied.add(newborn)
                        next_id += 1
                        births += 1
                    assert wealth == available
                    agents[identity] = (target, wealth, age)
                actions += 1
            else:
                assert kind == 'E' and numbers == [cycle] and not expected
                landscape = [min(4, value + 1) for value in landscape]
                assert len(occupied) == len(agents) == len({a[0] for a in agents.values()})
                row = next(metrics)
                wealths = sorted(a[1] for a in agents.values())
                total = sum(wealths)
                n = len(agents)
                assert int(row['cycle']) == cycle and int(row['population']) == n
                assert int(row['wealth']) == total and int(row['landscape']) == sum(landscape)
                assert int(row['births']) == births and int(row['deaths']) == deaths
                mean_age = sum(a[2] for a in agents.values()) / n if n else 0
                assert abs(float(row['mean_age']) - mean_age) < 1e-10
                # Pairwise absolute differences, reduced via sorted prefixes rather than the native weighted formula.
                prefix = distance_sum = 0
                for i, value in enumerate(wealths):
                    distance_sum += i * value - prefix
                    prefix += value
                gini = distance_sum / (n * total) if total else 0
                assert abs(float(row['gini']) - gini) < 1e-12
                total_births += births
                total_deaths += deaths
                births = deaths = 0
                expected = set(agents)
                cycle += 1
        assert list(metrics) == [] and cycle == protocol['cycles'] + 1
    tape_path = root / f'{scenario}-observed.observations.tape'
    with tape_path.open('rb') as inp, gzip.open(str(tape_path) + '.gz', 'xb') as out:
        for block in iter(lambda: inp.read(1024 * 1024), b''):
            out.write(block)
    with gzip.open(str(tape_path) + '.gz', 'rb') as inp:
        assert hashlib.file_digest(inp, 'sha256').hexdigest() == hashlib.sha256(tape_path.read_bytes()).hexdigest()
    reports.append({'scenario': scenario, 'cycles': cycle - 1, 'actions': actions,
                    'births': total_births, 'deaths': total_deaths,
                    'native_outputs_byte_identical': True, 'all_actions_replayed': True})
    print(json.dumps(reports[-1]), flush=True)
hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(root.iterdir()) if p.is_file()}
(root / 'audit.json').write_text(json.dumps({'runs': reports, 'hashes': hashes, 'scope': protocol['scope']}, indent=2) + '\n')
