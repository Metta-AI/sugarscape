import csv
from pathlib import Path
import sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
root=Path(sys.argv[1])
with (root/'cdfs.csv').open() as stream: rows=list(csv.DictReader(stream))
fig,axes=plt.subplots(1,2,figsize=(9,4),sharey=True)
for ax,name,title in zip(axes,['metabolism','wealth'],['Metabolism shapes (2, 5)','Wealth shapes (5, 2)'],strict=True):
 selected=[r for r in rows if r['parameter']==name]
 x=[float(r['unit_value']) for r in selected]
 for metric,label,color,style in [('native_cdf','Native sampler','#0072B2','-'),('beta_cdf','Beta law stated in paper','#D55E00','--'),('empirical_cdf','300 native initial agents','#666666',':')]:
  ax.plot(x,[float(r[metric]) for r in selected],style,color=color,label=label)
 ax.set(title=title,xlabel='Value before native scaling',xlim=(0,1),ylim=(0,1))
 ax.grid(alpha=.2)
axes[0].set_ylabel('Cumulative probability')
fig.legend(*axes[0].get_legend_handles_labels(),loc='lower center',ncol=3,frameon=False,fontsize=8)
fig.suptitle('Quera initialization: native sampler versus stated distribution')
fig.tight_layout(rect=(0,.08,1,.95))
for extension in ['png','pdf']:fig.savefig(root/('initialization-cdfs.'+extension),dpi=180)
plt.close(fig)
