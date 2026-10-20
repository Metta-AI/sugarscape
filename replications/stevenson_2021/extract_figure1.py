"""Recover approximate Figure 1 curves from the original vector PDF and labeled axes."""
import argparse
import csv
import gzip
import hashlib
import io
import json
from pathlib import Path
import re
import subprocess
import xml.etree.ElementTree as ET

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('pdf', type=Path)
parser.add_argument('output', type=Path)
args = parser.parse_args()
assert hashlib.sha256(args.pdf.read_bytes()).hexdigest() == '794b5f8f9e26098918579fed7c3418622a078d986d5c1bc2e26597439a3f2a47'
args.output.mkdir(parents=True, exist_ok=False)
svg = args.output / 'figure1.svg'
subprocess.run(['pdftocairo', '-svg', str(args.pdf.resolve()), str(svg.resolve())], check=True)
paths = ET.parse(svg).findall('.//{http://www.w3.org/2000/svg}path')
# Tick anchors inspected in the original figure. Rotation exchanges SVG x/y roles.
assert paths[153].attrib['d'] == 'M 2663.984375 373.320312 L 2663.984375 2506.796875 '
assert paths[370].attrib['d'] == 'M 2663.984375 3253.28125 L 2663.984375 5386.71875 '
assert paths[160].attrib['d'] == 'M 2581.601562 288.007812 L 659.609375 288.007812 '
assert paths[377].attrib['d'] == 'M 2583.710938 3168.007812 L 698.515625 3168.007812 '
assert paths[490].attrib['d'] == 'M 2581.289062 5471.992188 L 510.585938 5471.992188 '
curves = []
for name, start, stop, color, t0, t1, y0, y1, value_max in [
    ('elite_age_low_fertility',103,153,'rgb(0%, 0%, 0%)',373.320312,2506.796875,2581.601562,659.609375,8000),
    ('mean_age_low_fertility',166,216,'rgb(49.803162%, 49.803162%, 49.803162%)',373.320312,2506.796875,2581.601562,659.609375,8000),
    ('elite_age_birth_cost',216,266,'rgb(89.804077%, 89.804077%, 89.804077%)',373.320312,2506.796875,2581.601562,659.609375,8000),
    ('mean_age_birth_cost',266,316,'rgb(80.000305%, 80.000305%, 80.000305%)',373.320312,2506.796875,2581.601562,659.609375,8000),
    ('population_low_fertility',320,370,'rgb(89.804077%, 89.804077%, 89.804077%)',3253.28125,5386.71875,2583.710938,698.515625,800),
    ('population_birth_cost',383,433,'rgb(80.000305%, 80.000305%, 80.000305%)',3253.28125,5386.71875,2583.710938,698.515625,800),
    ('gini_low_fertility',433,483,'rgb(0%, 0%, 0%)',3253.28125,5386.71875,2581.289062,510.585938,.8),
    ('gini_birth_cost',496,546,'rgb(49.803162%, 49.803162%, 49.803162%)',3253.28125,5386.71875,2581.289062,510.585938,.8),
]:
    vertices = []
    for path in paths[start:stop]:
        assert path.attrib['stroke'] == color
        assert path.attrib['transform'] == 'matrix(0.1, 0, 0, -0.1, 0, 576)'
        d = path.attrib['d']
        assert re.sub(r'[ML] [0-9.]+ [0-9.]+\s*','',d) == ''
        points = [(float(x),float(y)) for x,y in re.findall(r'[ML] ([0-9.]+) ([0-9.]+)',d)]
        assert len(points)>100
        vertices.extend(((y-t0)/(t1-t0)*50000,(y0-x)/(y0-y1)*value_max) for x,y in points)
    assert all(a[0]<=b[0] for a,b in zip(vertices,vertices[1:]))
    assert abs(vertices[0][0])<5 and abs(vertices[-1][0]-50000)<5
    stream=io.StringIO();writer=csv.writer(stream);writer.writerow(['approximate_cycle','approximate_value']);writer.writerows(vertices)
    target=args.output/(name+'.csv.gz');target.write_bytes(gzip.compress(stream.getvalue().encode(),mtime=0))
    # Integrate segments, not vertices: the export omits some collinear points.
    begin,end=35000.,min(50000.,vertices[-1][0]);area=0.
    for (ta,va),(tb,vb) in zip(vertices,vertices[1:]):
        if tb<=ta or tb<=begin or ta>=end: continue
        left,right=max(ta,begin),min(tb,end)
        lv=va+(vb-va)*(left-ta)/(tb-ta);rv=va+(vb-va)*(right-ta)/(tb-ta)
        area+=(lv+rv)/2*(right-left)
    curves.append({'series':name,'vertices':len(vertices),'first_cycle':vertices[0][0],
                   'last_cycle':vertices[-1][0],'late_window':[begin,end],
                   'late_piecewise_linear_mean':area/(end-begin),'terminal_value':vertices[-1][1],
                   'csv_gzip_sha256':hashlib.sha256(target.read_bytes()).hexdigest()})
report={'pdf_sha256':hashlib.sha256(args.pdf.read_bytes()).hexdigest(),'svg_sha256':hashlib.sha256(svg.read_bytes()).hexdigest(),
        'curves':curves,'method':'Axes calibrated from inspected tick labels, not fitted to our simulations. Preserve all exported vertices and duplicated coordinates; summarize by segment integration.',
        'limits':'Approximate vector digitization, not raw simulation data. Unknown published seed and aggregation. Collinear points omitted by export; rounded coordinates prevent exact per-cycle recovery. Late windows are descriptive, not predeclared paper acceptance criteria.'}
(args.output/'extraction.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(curves))
