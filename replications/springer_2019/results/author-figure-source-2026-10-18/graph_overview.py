# a stacked bar plot with errorbars
#from matplotlib import rcParams

import numpy as np
import matplotlib.pyplot as plt

import matplotlib.font_manager
#print(matplotlib.font_manager.findSystemFonts(fontpaths=None, fontext='ttf'))
print(plt.style.available)

import matplotlib as mpl
mpl.rcParams['hatch.linewidth'] = 0.25

fsize = 10
plt.style.use('ggplot')
plt.style.use('seaborn-paper')

plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['FreeSans']
plt.rcParams['font.size'] = fsize
plt.rcParams['image.cmap'] = 'jet'

plt.figure(figsize=(10,3.2))

N = 8
xcolor = 'white'
soaalloc_total = list(map(lambda x: x/1000, [25814, 85610, 2188, 63080, 133349, 85704, 59801, 3685]))
soaalloc_enum = list(map(lambda x: x/1000, [8429, 661, 96, 329, 8331, 8492, 2847, 139]))
soaalloc = list(map(lambda x: x[0]-x[1], zip(soaalloc_total,soaalloc_enum)))

mallocmc_total = list(map(lambda x: x/1000, (161180, 105425, 232469, 168142, 160971, 128306,241459,252757)))
mallocmc_enum = list(map(lambda x: x/1000, (106763, 372, 230530, 186, 28488, 38794,55037 ,218482)))
mallocmc = list(map(lambda x: x[0]-x[1], zip(mallocmc_total,mallocmc_enum)))

halloc_total = list(map(lambda x: x/1000, (167870, 130192,234142,182909,212121,128282,181553,226153)))
halloc_enum = list(map(lambda x: x/1000, (107397, 368,231924, 182,28583,38716,55332,220270)))
halloc = list(map(lambda x: x[0]-x[1], zip(halloc_total,halloc_enum)))

bitmap_total = list(map(lambda x: x/1000, (38963, 109126,3239,151005,139970,93760,81298,4772)))
bitmap_enum = list(map(lambda x: x/1000, (9157, 876,174, 501,14471,11416,4998,251)))
bitmap = list(map(lambda x: x[0]-x[1], zip(bitmap_total,bitmap_enum)))

#BARNES: (2441544, 106085)
#SUGARSCAPE: (857074, 36435)
#GOL: (561928, 230971)
cuda_total = list(map(lambda x: x/1000, (260000, 116147,265000,193059,260000,260000,260000,260000)))
cuda_enum = list(map(lambda x: x/1000, (0, 364,179, 187,9,0,0,0)))
cuda = list(map(lambda x: x[0]-x[1], zip(cuda_total,cuda_enum)))

baseline_soa = list(map(lambda x: x/1000, (0, 133513,0,87680,113777,62597,48542,2677)))
baseline_aos = list(map(lambda x: x/1000, (0, 206870,0,192222,110820,253198,79917,14382)))
#traffic_aos: 109863


ind = np.arange(N)    # the x locations for the groups
width = 0.11      # the width of the bars: can also be len(x) sequence

soaalloc_1 = plt.bar(ind, soaalloc, width,edgecolor='black', hatch='////')
soaalloc_2 = plt.bar(ind, soaalloc_enum, width,color=xcolor,
             bottom=soaalloc,edgecolor='black')

mallocmc_1 = plt.bar(ind+width, mallocmc, width, edgecolor="black", hatch='XXXX')
mallocmc_2 = plt.bar(ind+width, mallocmc_enum, width, color=xcolor, edgecolor="black",
             bottom=mallocmc)

halloc_1 = plt.bar(ind+2*width, halloc, width, edgecolor="black",hatch='OO',)
halloc_2 = plt.bar(ind+2*width, halloc_enum, width, color=xcolor, edgecolor="black",
             bottom=halloc)

bitmap_1 = plt.bar(ind+3*width, bitmap, width, edgecolor="black", hatch='\\\\\\\\')
bitmap_2 = plt.bar(ind+3*width, bitmap_enum, width, color=xcolor, edgecolor="black",
             bottom=bitmap)

cuda_1 = plt.bar(ind+4*width, cuda, width, edgecolor="black", hatch='**')
cuda_2 = plt.bar(ind+4*width, cuda_enum, width, color=xcolor, edgecolor="black",
             bottom=cuda)

baseline_soa_1 = plt.bar(ind+5*width, baseline_soa, width, edgecolor="black", hatch='++++')
baseline_aos_1 = plt.bar(ind+6*width, baseline_aos, width, edgecolor="black", hatch='....')

plt.ylabel('Running Time (seconds)', size=fsize)
plt.xticks(ind+3*width, ('barnes-hut', 'collision', 'game-of-life', 'nbody', 'structure', 'sugarscape', 'traffic', 'wa-tor'), size=fsize)

#plt.text(soaalloc_1[1].get_x(), soaalloc_1[1].get_y()+40, str(soaalloc_total[1]), rotation=90)
plt.text(baseline_soa_1[0].get_x(), baseline_soa_1[0].get_y()+5, "n/a", rotation=90, multialignment='left', verticalalignment='bottom')
plt.text(baseline_aos_1[0].get_x(), baseline_aos_1[0].get_y()+5, "n/a", rotation=90, multialignment='left', verticalalignment='bottom')
plt.text(cuda_1[0].get_x(), cuda_2[0].get_y()+5, "... 2441.5", rotation=0, horizontalalignment='center', verticalalignment='bottom')
plt.text(cuda_1[5].get_x(), cuda_2[5].get_y()+5, "... 857.1", rotation=0, horizontalalignment='center', verticalalignment='bottom')
plt.text(cuda_1[2].get_x(), cuda_2[2].get_y()+5, "... 561.9", rotation=0, horizontalalignment='center', verticalalignment='bottom')
plt.text(cuda_1[4].get_x(), cuda_2[4].get_y()+5, "... 7345.4", rotation=0, horizontalalignment='center', verticalalignment='bottom')
plt.text(cuda_1[6].get_x(), cuda_2[6].get_y()+5, "... 9541.4", rotation=0, horizontalalignment='center', verticalalignment='bottom')
plt.text(cuda_1[7].get_x(), cuda_2[7].get_y()+5, "... 1012.3", rotation=0, horizontalalignment='center', verticalalignment='bottom')

#1100307

plt.text(baseline_soa_1[2].get_x(), baseline_soa_1[2].get_y()+5, "n/a", rotation=90, multialignment='left', verticalalignment='bottom')
plt.text(baseline_aos_1[2].get_x(), baseline_aos_1[2].get_y()+5, "n/a", rotation=90, multialignment='left', verticalalignment='bottom')
plt.text(soaalloc_1[2].get_x(), soaalloc_2[2].get_y()+5, "2.2", rotation=90, multialignment='left', verticalalignment='bottom')
plt.text(bitmap_1[2].get_x(), bitmap_2[2].get_y()+5, "3.2", rotation=90, multialignment='left', verticalalignment='bottom')


plt.text(soaalloc_1[7].get_x(), soaalloc_2[7].get_y()+5, str('3.7'), rotation=90, multialignment='left', verticalalignment='bottom')
plt.text(bitmap_1[7].get_x()+0.01, bitmap_2[7].get_y()+5, str('4.8'), rotation=90, multialignment='left', verticalalignment='bottom')
plt.text(baseline_soa_1[7].get_x(), baseline_soa_1[7].get_y()+5+1.9, str('2.7'), rotation=90, multialignment='left', verticalalignment='bottom')
plt.text(baseline_aos_1[7].get_x(), baseline_aos_1[7].get_y()+5+10.9, str('14.4'), rotation=90, multialignment='left', verticalalignment='bottom')

plt.text(-0.1, 325,'(lower is better)',
     horizontalalignment='left',
     verticalalignment='center')
     
#plt.yticks(np.arange(0, 81, 10))
plt.ylim(0, 345)
plt.xlim(-0.2,7.85)
plt.legend((soaalloc_1[0], mallocmc_1[0], halloc_1[0], bitmap_1[0], cuda_1[0], baseline_soa_1[0],baseline_aos_1[0],soaalloc_2[0]), ('DynaSOAr', 'MallocMC', 'Halloc', 'BitmapAlloc', 'CUDA Allocator', 'Baseline (SOA)', 'Baseline (AOS)', 'Par. Enumeration'),fancybox=False, ncol=4, prop={'size': fsize})
plt.show()
