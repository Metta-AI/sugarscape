"""Decode original founder-wealth vector paths without inventing unlabelled agent identities."""
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

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('pdf',type=Path)
parser.add_argument('output',type=Path)
args=parser.parse_args()
assert hashlib.sha256(args.pdf.read_bytes()).hexdigest()=='c87edebc4f6296cc37fa367502bb8e8d761ded2fc4ef3ff6b89d0ad024c7f71a'
args.output.mkdir(parents=True,exist_ok=False)
svg=args.output/'figure2.svg'
subprocess.run(['pdftocairo','-svg',str(args.pdf.resolve()),str(svg.resolve())],check=True)
paths=ET.parse(svg).findall('.//{http://www.w3.org/2000/svg}path')
assert paths[166].attrib['d']=='M 2591.992188 520 L 2591.992188 2741.484375 '
assert paths[175].attrib['d']=='M 2517.304688 431.992188 L 665.507812 431.992188 '
assert paths[199].attrib['d']=='M 2591.992188 3328.007812 L 2591.992188 5272.8125 '
assert paths[206].attrib['d']=='M 2517.304688 3240 L 876.289062 3240 '
curves=[]
first_founder_drops=[]
for scenario,black,gray,t0,t1,max_time,w0,w1,max_wealth in [
    ('low-fertility',range(101,136),range(136,166),520.,2741.484375,35000.,2517.304688,665.507812,500.),
    ('birth-cost',range(184,187),range(187,199),3328.007812,5272.8125,5000.,2517.304688,876.289062,80.),
]:
    groups=[('founder-0',list(black)),*[(f'unlabelled-{i+1}',[index]) for i,index in enumerate(gray)]]
    for label,indices in groups:
        points=[]
        for index in indices:
            path=paths[index]
            assert path.attrib['transform']=='matrix(0.1, 0, 0, -0.1, 0, 576)'
            assert path.attrib['stroke']==('rgb(0%, 0%, 0%)' if label=='founder-0' else 'rgb(74.510193%, 74.510193%, 74.510193%)')
            encoded=path.attrib['d'];assert re.sub(r'[ML] [0-9.]+ [0-9.]+\s*','',encoded)==''
            points.extend(((float(y)-t0)/(t1-t0)*max_time,(w0-float(x))/(w0-w1)*max_wealth)
                          for x,y in re.findall(r'[ML] ([0-9.]+) ([0-9.]+)',encoded))
        assert all(a[0]<=b[0] for a,b in zip(points,points[1:]))
        assert all(t>=0 and w>=-.01 for t,w in points)
        stream=io.StringIO();writer=csv.writer(stream);writer.writerow(['approximate_cycle','approximate_wealth']);writer.writerows(points)
        filename=f'{scenario}-{label}.csv.gz';data=gzip.compress(stream.getvalue().encode(),mtime=0);(args.output/filename).write_bytes(data)
        curves.append({'scenario':scenario,'label':label,'source_path_indices':indices,'vertices':len(points),
                       'first_cycle':points[0][0],'last_cycle':points[-1][0],
                       'maximum_integer_wealth_rounding_distance':max(abs(w-round(w)) for t,w in points),
                       'filename':filename,'gzip_sha256':hashlib.sha256(data).hexdigest()})
        if scenario=='birth-cost' and label=='founder-0':
            first_founder_drops=[{'before_cycle':a[0],'before_wealth':a[1],'after_cycle':b[0],'after_wealth':b[1]}
                                 for a,b in zip(points,points[1:]) if b[1]-a[1]<-25]
report={'pdf_sha256':hashlib.sha256(args.pdf.read_bytes()).hexdigest(),'svg_sha256':hashlib.sha256(svg.read_bytes()).hexdigest(),
        'curves':curves,'birth_cost_founder0_large_drops':first_founder_drops,
        'trace_counts':{'low_fertility':31,'birth_cost':13},
        'caption_counts':{'low_fertility':30,'birth_cost':12},
        'identity_limit':'Black paths identify founder zero. Grey traces are distinct vector paths without individual labels; their ordinal labels are not asserted agent IDs.',
        'interpretation':'Approximate published trajectories, not simulation replay. First founder birth-cost drop at approximately cycle41 is compatible with either threshold rule because fertility is stochastic. Do not infer a historical rule from this event.'}
(args.output/'extraction.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'curves':len(curves),'vertices':sum(row['vertices'] for row in curves),'first_drop':first_founder_drops[0]}))
