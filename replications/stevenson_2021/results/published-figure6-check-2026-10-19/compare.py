from pathlib import Path
import csv,hashlib,json
import fitz,numpy as np
p=Path(__file__).resolve().parent
src=Path('/Users/relh/Code/workspace/sugarscape-stevenson/replications/stevenson_2021/results/figure6-recurrence-2026-10-16')
pix=fitz.Pixmap(str(p/'figure6.png'))
assert (pix.width,pix.height,pix.n)==(685,366,1)
im=np.frombuffer(pix.samples,dtype=np.uint8).reshape(366,685)
ys,xs=np.nonzero(im<150)
keep=(xs>=403)&(xs<=684)&(ys>=60)&(ys<=322)&~((xs>=510)&(xs<=650)&(ys>=252)&(ys<=301))
xs=xs[keep];ys=ys[keep]
rows=[]
for f in sorted(src.glob('rate-*.csv')):
 for r in csv.DictReader(f.open()):
  t=float(r['approximate_cycle']);n=float(r['approximate_population']);x=403+t*271/80;y=327-n*249/1000
  excluded=n<25 or (510<=x<=650 and 252<=y<=301) or not(403<=x<=684 and 60<=y<=322)
  row={'rate':f.stem[5:],'cycle':t,'population':n,'pixel_x':x,'pixel_y':y,'excluded_axis_legend_or_viewport':excluded,'nearest_dark_pixel_distance':''}
  if not excluded:row['nearest_dark_pixel_distance']=float(np.sqrt(np.min((xs-x)**2+(ys-y)**2)))
  rows.append(row)
with (p/'vertex-distance-002.csv').open('x') as file:
 w=csv.DictWriter(file,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
values=[r['nearest_dark_pixel_distance'] for r in rows if not r['excluded_axis_legend_or_viewport']]
a={'publisher_image_sha256':hashlib.sha256((p/'figure6.png').read_bytes()).hexdigest(),'axis_registration':{'cycle0_x':403,'cycle80_x':674,'population0_y':327,'population1000_y':78},'vertices_total':len(rows),'vertices_examined':len(values),'excluded':len(rows)-len(values),'median_nearest_ink_distance_pixels':float(np.median(values)),'maximum_nearest_ink_distance_pixels':max(values),'within_two_pixels':sum(v<=2 for v in values),'limits':['Exploratory one-way proximity to all dark pixels, not curve identity or independent observations.','Dotted and overlapping curves are not individually identifiable; axes, legend and near-zero vertices are excluded.','Manual raster registration and antialiasing prevent exact numerical equivalence claims.'],'visual_assessment':'Same panel structure, four rate labels and recognizable curve shapes as preprint; no evident redraw of trajectories.','scope':'Published equation correction supported separately; delay ambiguity remains.'}
(p/'audit.json').write_text(json.dumps(a,indent=2)+'\n')
print(json.dumps(a,indent=2))
