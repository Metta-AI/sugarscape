from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
r=Path(__file__).resolve().parent
fig,axes=plt.subplots(2,3,figsize=(12,7),layout='constrained')
names=['Population','Mean time to live','Deaths / population','Mean age at death','Total wealth','Wealth / population']
for f,ax,title in zip(range(4,10),axes.flat,names,strict=True):
    a=np.loadtxt(r/f'figure-{f}-egoistic.csv',delimiter=',',skiprows=1)
    ax.plot(a[:,0],a[:,3],color='#009caa',linewidth=2,label='Published Egoist path')
    ax.plot(a[:,0],a[:,4],color='#174a7e',linewidth=0.8,linestyle='--',label='Released parser reproduction')
    if f==6:
        d=np.loadtxt(r/'all-cause-deaths.csv',delimiter=',',skiprows=1)
        ax.plot(d[:,0],d[:,-1],color='#a02040',linewidth=0.8,linestyle=':',label='All-cause reproduction')
    ax.set(title=f'Figure {f}: {title}',xlabel='Timestep',xlim=(0,5000))
    ax.grid(alpha=.2)
axes.flat[2].legend(fontsize=7)
fig.suptitle('Egoist: 500 original seeds — published vector paths versus native reproduction')
fig.savefig(r/'comparison.png',dpi=150)
fig.savefig(r/'comparison.pdf')
