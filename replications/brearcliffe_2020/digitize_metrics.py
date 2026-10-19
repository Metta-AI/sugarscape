"""Extract visible endpoint bounds for manuscript Figures 4–9."""

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
inventory = json.loads(Path(__file__).with_name('figure-panel-inventory.json').read_text())
assert hashlib.sha256(args.paper.read_bytes()).hexdigest() == inventory['paper_sha256']
document = fitz.open(args.paper)
# Calibrate only against labelled, strictly positive major grid lines.
# The bottom labels rounded to zero in Figures 6–9 are not calibration anchors.
calibrations = {
    4: ('mean vision', 1, 208),
    5: ('mean metabolism', 1, 208),
    6: ('cumulative combat deaths', 5, 179),
    7: ('cumulative starvation deaths', 5, 179),
    8: ('mean age', 4, 173),
    9: ('maximum age', 5, 179),
}
figures = []
for figure in inventory['figures'][1:]:
    metric, top_exponent, unit_row = calibrations[figure['figure']]
    records = []
    axis_strips = set()
    for panel in figure['panels']:
        encoded = document.extract_image(panel['xref'])['image']
        assert hashlib.sha256(encoded).hexdigest() == panel['sha256']
        pixmap = fitz.Pixmap(encoded)
        assert (pixmap.width, pixmap.height, pixmap.n) == (308, 243, 3)
        pixels = np.frombuffer(pixmap.samples, dtype=np.uint8).reshape(243, 308, 3)
        axis_strips.add(hashlib.sha256(pixels[28:214, :16].tobytes()).hexdigest())
        red, green, blue = pixels.astype(int).transpose(2, 0, 1)
        masks = {'A': (blue > red + 30) & (blue > green + 10),
                 'B': (red > green + 30) & (red > blue + 30)}
        for breed, mask in masks.items():
            ys = np.flatnonzero(mask[30:210, 302]) + 30
            record = {'group_A': panel['group_A'], 'group_B': panel['group_B'],
                      'breed': breed, 'panel_sha256': panel['sha256'],
                      'column': 302, 'visible_pixel_rows': ys.tolist()}
            if len(ys) == 0:
                record['status'] = 'unresolved-no-visible-color-at-endpoint'
            else:
                assert np.max(np.diff(ys), initial=0) <= 1, record
                record['status'] = 'visible-raster-interval-not-statistical-confidence'
                # One extra pixel bounds raster stroke and grid calibration resolution.
                record['metric_interval'] = [
                    10 ** ((unit_row - (float(ys.max()) + 1)) * top_exponent / (unit_row - 33)),
                    10 ** ((unit_row - (float(ys.min()) - 1)) * top_exponent / (unit_row - 33)),
                ]
            records.append(record)
    assert len(records) == 32 and len(axis_strips) == 1
    figures.append({'figure': figure['figure'], 'metric': metric,
                    'calibration': {'axis': 'log10', 'top_grid_y': 33,
                                    'top_value': 10 ** top_exponent, 'unit_grid_y': unit_row,
                                    'unit_value': 1, 'additional_pixel_margin': 1,
                                    'identical_axis_strip_sha256': next(iter(axis_strips))},
                    'records': records})
result = {'paper_sha256': inventory['paper_sha256'], 'figures': figures,
          'limits': ['Column302 approximates the final tick; x-axis tick labels are absent.',
                     'Occluded curves are unresolved, never inferred equal to the visible curve.',
                     'Intervals describe raster resolution, not sampling uncertainty or acceptance margins.',
                     'Calibration uses printed positive labels; bottom labels rounded to zero are excluded.',
                     'No simulation results were used to choose calibration or color thresholds.']}
args.new_output.mkdir()
(args.new_output / 'metric-endpoints.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({'records': sum(len(f['records']) for f in figures),
                  'visible': sum('metric_interval' in r for f in figures for r in f['records'])}))
