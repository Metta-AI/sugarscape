"""Read the inspected Figure 3 lower-left panel; do not infer its timestep."""
import gzip
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image

root = Path(__file__).resolve().parent
image_path = root / 'figure-000.png'
image = np.asarray(Image.open(image_path)).astype(int)
assert image.shape == (602, 575, 3)
# Bounds inspected in the embedded PDF image, independently of replay outcomes.
# The displayed grid has 50 columns and 50 rows, matching released dimensions.
variants = []
for dy in [-0.5, 0, 0.5]:
    for dx in [-0.5, 0, 0.5]:
        blue = []
        red = []
        for y in range(50):
            for x in range(50):
                pixel = image[round(303 + (y + 0.5) * 299 / 50 + dy),
                              round((x + 0.5) * 287 / 50 + dx)]
                if pixel[2] > 180 and pixel[0] < 100 and pixel[1] < 100:
                    blue.append([x, y])
                if pixel[0] > 200 and pixel[1] < 100 and pixel[2] < 100:
                    red.append([x, y])
        variants.append({'offset_pixels': [dx, dy], 'blue': blue, 'red': red})
assert all(v['blue'] == variants[0]['blue'] and v['red'] == variants[0]['red'] for v in variants)
pdf = root.parent / 'papers/replacing-sugarscape-author-2023.pdf'
assert hashlib.sha256(pdf.read_bytes()).hexdigest() == 'e1d5bcec1ae247660293dd73af1bdeacc964f2db9ee3968161f26237a5f8012e'
comparisons = []
for name in ['replacing-2023-disease-observed-001', 'replacing-2023-preconference-disease-observed-001']:
    path = root.parent / name / 'summary.json'
    rows = json.loads(path.read_text())
    native = json.loads((path.parent / 'trajectory.json').read_text())
    with gzip.open(path.parent / 'observations.jsonl.gz', 'rt') as stream:
        observed = [json.loads(line) for line in stream]
    for row, state, logged in zip(rows, observed, native, strict=True):
        assert row['timestep'] == state['timestep'] == logged['timestep']
        assert row['population'] == len(state['agents']) == logged['population']
        assert row['infected'] == sum(agent[6] > 0 for agent in state['agents'])
    assert [r['timestep'] for r in rows] == list(range(501))
    comparisons.append({'evidence': name, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                        'observations': len(rows), 'minimum_population': min(r['population'] for r in rows),
                        'minimum_uninfected_population': min(r['population'] for r in rows if r['infected'] == 0),
                        'matching_population_observations': sum(r['population'] == len(variants[0]['blue']) for r in rows)})
report = {'pdf_sha256': hashlib.sha256(pdf.read_bytes()).hexdigest(),
          'embedded_image_sha256': hashlib.sha256(image_path.read_bytes()).hexdigest(),
          'pdf_page': 10, 'panel': 'lower left', 'bounds_xyxy': [0,303,287,602],
          'blue_agents': len(variants[0]['blue']), 'red_agents': len(variants[0]['red']),
          'sampling_sensitivity': variants, 'native_comparisons': comparisons,
          'interpretation': 'The displayed 18 healthy agents support roughly20 survivors in the prose. Neither tested 501-observation baseline contains this population. Screenshot time and historical source remain unknown; not a whole-paper negative replication.'}
(root / 'audit.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k != 'sampling_sensitivity'}))
