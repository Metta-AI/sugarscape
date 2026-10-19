# a stacked bar plot with errorbars
import numpy as np
import matplotlib.pyplot as plt

fsize=10

fig = plt.figure(figsize=(10,3.2))

N = 7
soaalloc_orig =  np.array([1, 0.92307, 0.96551, 0.78302, 1.6099131, 1.51865, 1.0671875])
soaalloc =  np.array([1, 0.92307, 0.96551, 0.78302, 1.6099131, 1.51865, 1.0671875])# / soaalloc_orig

#0.37265625
mallocmc = np.array([235000.0/300000, 0.726, 0.615, 0.43, 1.199669, 1.017102, 1632.0/9888])# / soaalloc_orig

bitmap = np.array([279000.0/300000, 1, 1, 0.5681, 1.5114532, 1.01710243, 1.076953125]) #/ soaalloc_orig

#0.6515625
halloc = np.array([0, 0, 0, 0.28125, 1.165129, 0.75506598, 4160.0/9888])#/ soaalloc_orig

baseline_soa = np.array([0, 1.02857, 1, 1.1832, 1.03225, 1, 1.00840336])#/soaalloc_orig
baseline_aos = np.array([0, 1,1,1,1,1,1])/soaalloc_orig



ind = np.arange(N)    # the x locations for the groups
width = 0.12       # the width of the bars: can also be len(x) sequence

soaalloc_1 = plt.bar(ind, soaalloc, width,edgecolor='black', hatch='////')

mallocmc_1 = plt.bar(ind+width, mallocmc, width, edgecolor="black", hatch='XXXX')

halloc_1 = plt.bar(ind+2*width, halloc, width, edgecolor="black",hatch='OO')
#halloc_2 = plt.bar(ind+2*width, halloc_enum, width, color="#FF8C00", edgecolor="black",
#             bottom=halloc, hatch='/')

bitmap_1 = plt.bar(ind+3*width, bitmap, width, edgecolor="black",hatch='\\\\\\\\')

#next(fig._get_lines.prop_cycler) 

baseline_soa_1 = plt.bar(ind+4*width, baseline_soa, width, color='#8eba42', edgecolor="black",hatch='++++')
baseline_aos_1 = plt.bar(ind+5*width, baseline_aos, width, color='#ffb5b8', edgecolor="black",hatch='....')

plt.ylabel('Max. problem size rel. to DynaSOAr', size=fsize)
plt.xticks(ind+3*width, ('barnes-hut', 'collision',  'nbody', 'structure', 'sugarscape', 'traffic', 'wa-tor'), size=fsize)
plt.xlim(-2*width, 6.85)
plt.hlines(1.0, -2*width, 6.85, colors=['green'], linestyles=['dashed'])

plt.text(halloc_1[0].get_x()+0.02, halloc_1[0].get_y()+0.675, "(n/a; heap too small)", rotation=90)
plt.text(halloc_1[1].get_x()+0.02, halloc_1[1].get_y()+0.675, "(n/a; heap too small)", rotation=90)
plt.text(halloc_1[2].get_x()+0.02, halloc_1[2].get_y()+0.675, "(n/a; heap too small)", rotation=90)
plt.text(baseline_soa_1[0].get_x(), baseline_soa_1[0].get_y()+0.02, "n/a", rotation=90, multialignment='left', verticalalignment='bottom')
plt.text(baseline_aos_1[0].get_x(), baseline_aos_1[0].get_y()+0.02, "n/a", rotation=90, multialignment='left', verticalalignment='bottom')

plt.text(6.75, 1.5,'(higher is better)',
     horizontalalignment='right',
     verticalalignment='center')
#plt.yticks(np.arange(0, 81, 10))
plt.legend((soaalloc_1[0], mallocmc_1[0],  halloc_1[0], bitmap_1[0], baseline_soa_1[0],baseline_aos_1[0]), ('DynaSOAr', 'MallocMC', 'Halloc', 'BitmapAlloc', 'Baseline (SOA)', 'Baseline (AOS)'),fancybox=False, loc=2, ncol=3, prop={'size': fsize})
plt.show()
