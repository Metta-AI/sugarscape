"""Execute a disjoint interval of an original deposited runtime model/horizon group."""
import argparse
import gzip
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
from typing import Literal
import zipfile

from pydantic import BaseModel, ConfigDict, Field

Model = Literal['rawSugarscape', 'altruisticHalfLookaheadBinary', 'egoisticHalfLookaheadBinary', 'benthamHalfLookaheadBinary']


class Configuration(BaseModel):
    model_config = ConfigDict(extra='allow', strict=True)
    seed: int = Field(ge=0)
    agentDecisionModels: list[Model] = Field(min_length=1, max_length=1)
    timesteps: Literal[500, 5000, 50000]
    startingAgents: Literal[250]
    startingDiseases: Literal[50]
    headlessMode: Literal[True]
    logfile: str


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('engine', type=Path)
parser.add_argument('archive', type=Path)
parser.add_argument('model', choices=['rawSugarscape', 'altruisticHalfLookaheadBinary', 'egoisticHalfLookaheadBinary', 'benthamHalfLookaheadBinary'])
parser.add_argument('steps', type=int, choices=[500, 5000, 50000])
parser.add_argument('output', type=Path)
parser.add_argument('--start', type=int, default=0)
parser.add_argument('--stop', type=int, default=100)
parser.add_argument('--seconds', type=int, default=7200)
args = parser.parse_args()
assert 0 <= args.start < args.stop <= 100 and 0 < args.seconds <= 21600
assert sys.version_info[:3] == (3, 11, 14)
engine = args.engine.resolve()
release = 'b9ca671ab7591c7b3606f2d76c33eda344d626d1'
assert subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=engine, text=True).strip() == release
assert not subprocess.check_output(['git', 'status', '--porcelain', '--untracked-files=no'], cwd=engine, text=True).strip()
archive_hash = hashlib.sha256(args.archive.read_bytes()).hexdigest()
assert archive_hash == '43b1967e9af9d7aac9785258706fd5abec6257235940b85aa811519c0e6ae98a'
with zipfile.ZipFile(args.archive) as archive:
    inputs = {name: archive.read(name) for name in archive.namelist() if name.startswith(f'{args.steps}-{args.model}')}
entries = sorted(inputs)
assert len(entries) == 100
assert len({json.loads(raw)['seed'] for raw in inputs.values()}) == 100
pins_path = Path(__file__).with_name('source-sha256.json')
pins = json.loads(pins_path.read_text())
source_hashes = {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in sorted(engine.glob('*.py'))}
assert source_hashes == pins['source_sha256']
defaults = json.loads((engine / 'config.json').read_text())['sugarscapeOptions']
for entry in entries:
    config = json.loads(inputs[entry])
    validated = Configuration.model_validate(config)
    assert validated.model_dump() == config and config.keys() == defaults.keys()
    assert config['agentDecisionModels'] == [args.model] and config['timesteps'] == args.steps
    assert entry == f'{args.steps}-{args.model}{config["seed"]}.config'
assert shutil.disk_usage(args.output.parent).free >= 2 * 1024**3
args.output.mkdir(parents=True, exist_ok=False)
root = args.output.resolve()
(root / 'run_runtime.py').write_bytes(Path(__file__).read_bytes())
(root / 'source-sha256.json').write_bytes(pins_path.read_bytes())
manifest = {'release': release, 'archive_sha256': archive_hash, 'model': args.model, 'steps': args.steps,
            'start': args.start, 'stop': args.stop, 'entries': entries[args.start:args.stop],
            'order': 'lexicographic archive filename', 'source_sha256': source_hashes, 'engine': str(engine),
            'python_executable': sys.executable, 'python': sys.version, 'pythonhashseed': '0',
            'timeout_seconds': args.seconds, 'runner_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
(root / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
started = time.monotonic()
with (root / 'completed.jsonl').open('x') as ledger:
    for index in range(args.start, args.stop):
        remaining = args.seconds - (time.monotonic() - started)
        assert remaining > 0 and shutil.disk_usage(root).free >= 2 * 1024**3
        assert all(hashlib.sha256((engine / name).read_bytes()).hexdigest() == digest for name, digest in source_hashes.items())
        entry = entries[index]
        output = root / entry.removesuffix('.config')
        output.mkdir()
        original = inputs[entry]
        configuration = json.loads(original)
        (output / 'original.config').write_bytes(original)
        configuration['logfile'] = str(output / 'trajectory.json')
        (output / 'config.json').write_text(json.dumps(configuration, indent=2) + '\n')
        command = [sys.executable, str(engine / 'sugarscape.py'), '--conf', str(output / 'config.json')]
        (output / 'command.json').write_text(json.dumps(command) + '\n')
        condition_started = time.monotonic()
        with (output / 'stdout.log').open('x') as stdout, (output / 'stderr.log').open('x') as stderr:
            result = subprocess.run(command, cwd=engine, env={**os.environ, 'PYTHONHASHSEED': '0', 'PYTHONDONTWRITEBYTECODE': '1'},
                                    stdout=stdout, stderr=stderr, timeout=remaining)
        (output / 'exit.json').write_text(json.dumps({'exit_code': result.returncode}) + '\n')
        result.check_returncode()
        raw = (output / 'trajectory.json').read_bytes()
        rows = json.loads(raw)
        assert [row['timestep'] for row in rows] == list(range(len(rows)))
        assert rows[-1]['timestep'] == args.steps or rows[-1]['population'] == 0
        compressed = gzip.compress(raw, mtime=0)
        assert gzip.decompress(compressed) == raw
        (output / 'trajectory.json.gz').write_bytes(compressed)
        record = {'index': index, 'entry': entry, 'seed': configuration['seed'], 'exit_code': 0,
                  'observations': len(rows), 'final_timestep': rows[-1]['timestep'], 'final_population': rows[-1]['population'],
                  'elapsed_seconds': time.monotonic() - condition_started,
                  'files_sha256': {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in sorted(output.iterdir())}}
        ledger.write(json.dumps(record) + '\n')
        ledger.flush()
        print(index, entry, record['final_population'], flush=True)
(root / 'complete.json').write_text(json.dumps({'completed_runs': args.stop - args.start}) + '\n')
