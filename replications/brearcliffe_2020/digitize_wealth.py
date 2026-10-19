"""Extract visible endpoint pixel bounds from the author manuscript's Figure 3."""

import argparse
import hashlib
import json
from pathlib import Path

import fitz
import numpy as np

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('paper', type=Path)
parser.add_argument('new_output', type=Path)
args = parser.parse_args()
inventory = json.loads((Path(__file__).parent / 'figure-panel-inventory.json').read_text())
assert hashlib.sha256(args.paper.read_bytes()).hexdigest() == inventory['paper_sha256']
args.new_output.mkdir()
document = fitz.open(args.paper)
figure = inventory['figures'][0]
assert figure['figure'] == 3
records = []
for panel in figure['panels']:
    encoded = document.extract_image(panel['xref'])['image']
    assert hashlib.sha256(encoded).hexdigest() == panel['sha256']
    pixmap = fitz.Pixmap(encoded)
    assert (pixmap.width, pixmap.height, pixmap.n) == (308, 243, 3)
    pixels = np.frombuffer(pixmap.samples, dtype=np.uint8).reshape(243, 308, 3).astype(int)
    red, green, blue = pixels[:, :, 0], pixels[:, :, 1], pixels[:, :, 2]
    masks = {'A': (blue > red + 30) & (blue > green + 10),
             'B': (red > green + 30) & (red > blue + 30)}
    for breed, mask in masks.items():
        # Final plotted column, excluding frame, axes and legend.
        ys = np.flatnonzero(mask[30:210, 302]) + 30
        record = {'group_A': panel['group_A'], 'group_B': panel['group_B'], 'breed': breed,
                  'panel_sha256': panel['sha256'], 'column': 302,
                  'visible_pixel_rows': ys.tolist()}
        if len(ys) == 0:
            record['status'] = 'unresolved-no-visible-color-at-endpoint'
        else:
            assert np.max(np.diff(ys), initial=0) <= 1, record
            # Manual major-grid calibration: y=33 is 10000; y=208 is 1.
            # Expand by one pixel for raster stroke/calibration uncertainty.
            low_y, high_y = float(ys.min()) - 1, float(ys.max()) + 1
            record['status'] = 'visible-raster-interval-not-statistical-confidence'
            record['wealth_interval'] = [10 ** ((208 - high_y) * 4 / 175),
                                         10 ** ((208 - low_y) * 4 / 175)]
        records.append(record)
result = {'figure': 3, 'metric': 'mean sugar', 'paper_sha256': inventory['paper_sha256'],
          'calibration': {'top_major_grid_y': 33, 'top_value': 10000,
                          'bottom_major_grid_y': 208, 'bottom_value': 1,
                          'axis': 'log10', 'additional_pixel_margin': 1},
          'limits': ['Raster endpoint at x302 approximates final plotted tick; source contains no visible x-axis tick labels.',
                     'Color occlusion can hide either breed; missing pixels are unresolved, not zero or equal to the visible breed.',
                     'Intervals express image resolution, not between-run uncertainty or a replication acceptance margin.',
                     'No simulation data was used to select calibration or pixel thresholds.'],
          'records': records}
(args.new_output / 'wealth-endpoints.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({'records': len(records), 'visible': sum('wealth_interval' in r for r in records)}))
