"""Independently compare the complete graphical and headless workflows."""
import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parent
baseline = root.parent / 'replacing-disease-matched-runtime-001'
report = []
for seed in [12345, 12881, 22744]:
    actual = root / str(seed)
    expected = baseline / f'archive-{seed}'
    config = json.loads((actual / 'config.json').read_text())
    original = json.loads((expected / 'config.json').read_text())
    changed = [k for k in original if config[k] != original[k]]
    assert set(changed) == {'headlessMode', 'logfile'}
    assert set(config) == set(original)
    assert config['headlessMode'] is False and original['headlessMode'] is True
    assert config['seed'] == seed and config['timesteps'] == 500
    assert json.loads((actual / 'exit.json').read_text())['exit_code'] == 0
    action = json.loads((actual / 'gui-action.json').read_text())
    assert action['window_exists'] == 1 and action['canvas_items'] == 2500
    assert action['color'] == 'Disease' and action['timestep'] == 0
    data = (actual / 'trajectory.json').read_bytes()
    assert data == (expected / 'trajectory.json').read_bytes()
    rows = json.loads(data)
    assert [r['timestep'] for r in rows] == list(range(501))
    report.append({'seed':seed, 'observations':len(rows), 'sha256':hashlib.sha256(data).hexdigest(),
                   'minimum_population':min(r['population'] for r in rows), 'final_population':rows[-1]['population'],
                   'configuration_changes':sorted(changed), 'byte_identical':True})
(root / 'independent-audit.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))
