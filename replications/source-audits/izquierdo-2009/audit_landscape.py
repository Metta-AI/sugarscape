import argparse
from pathlib import Path
import hashlib
import json
import numpy as np
from PIL import Image
from scipy.ndimage import label

parser = argparse.ArgumentParser()
parser.add_argument('figure1', type=Path)
parser.add_argument('figure2', type=Path)
parser.add_argument('comparison_map', type=Path)
parser.add_argument('output', type=Path)
args = parser.parse_args()
images = [np.asarray(Image.open(path).convert('RGB')) for path in (args.figure1, args.figure2)]
assert all(image.shape == (420,419,3) for image in images)
masks = [np.all(image == [255,255,0], axis=2) for image in images]
reports = []
interiors = []
for mask in masks:
    counts = mask[6:406,3:403].reshape(50,8,50,8).sum(axis=(1,3))
    assert counts.sum() == mask.sum()
    desert = counts == 0
    interior = desert.copy()
    for axis in (0,1):
        for direction in (-1,1):
            interior &= np.roll(desert,direction,axis=axis)
    interiors.append(interior)
    values, frequencies = np.unique(counts, return_counts=True)
    reports.append({'zero_capacity_cells': int(desert.sum()),
                    'cardinal_interior_desert_cells': int(interior.sum()),
                    'yellow_pixel_count_histogram': dict(zip(map(str,values), map(int,frequencies)))})
red = np.all(images[1] == [221,0,0], axis=2)
components, number = label(red)
assert number == 305 and np.all(np.bincount(components.flat)[1:] == 32)
red_grid = red[6:406,3:403].reshape(50,8,50,8).sum(axis=(1,3)) > 0
assert np.array_equal(red_grid,interiors[1])
comparison = np.loadtxt(args.comparison_map,dtype=int)
assert comparison.shape == (50,50) and set(np.unique(comparison)) == {0,1,2,3,4}
desert = comparison == 0
interior = desert.copy()
for axis in (0,1):
    for direction in (-1,1):
        interior &= np.roll(desert,direction,axis=axis)
report = {'figures': reports, 'highlighted_components': number,
          'figure2_highlights_equal_cardinal_desert_mask': True,
          'differing_yellow_pixels_yx': np.argwhere(masks[0] != masks[1]).tolist(),
          'differing_interior_cells_row_column': np.argwhere(interiors[0] != interiors[1]).tolist(),
          'comparison_map_interior_desert_cells': int(interior.sum()),
          'source_sha256': {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in (args.figure1,args.figure2,args.comparison_map)},
          'scope': 'Raster and topology audit only. No simulation, mixing-time estimate, or proof of ergodicity.'}
args.output.mkdir(exist_ok=False)
(args.output/'audit.json').write_text(json.dumps(report,indent=2)+'\n')
np.savetxt(args.output/'figure2-interior-desert-mask.csv',red_grid.astype(int),fmt='%d',delimiter=',')
print(json.dumps(report))
