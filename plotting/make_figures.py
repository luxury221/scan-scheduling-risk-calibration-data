"""Replot existing aggregate data for readable manuscript-sized panels."""
from pathlib import Path
import os
ROOT = Path(__file__).resolve().parent
os.environ['MPLCONFIGDIR'] = str(ROOT/'cache'/'matplotlib')
os.environ['TEMP'] = os.environ['TMP'] = str(ROOT/'tmp')
import csv
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

with (ROOT/'evidence'/'demand-calibration-workload-20261023--aggregate.csv').open(encoding='utf-8-sig',newline='') as f:
    data=list(csv.DictReader(f))
idx={(r['dataset'],int(r['nlist']),r['tag'],r['workload'],r['mode']):r for r in data}
methods=['complete','batch','merge','bits','value','frontier']
colors=['#555555','#999999','#0072B2','#009E73','#CC9A00','#D55E00']
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':8.5,'axes.titlesize':9,'axes.labelsize':8.5,
                     'xtick.labelsize':8,'ytick.labelsize':8,'pdf.fonttype':42,'ps.fonttype':42,
                     'axes.spines.top':False,'axes.spines.right':False})

def plot_settings(settings,name,rows):
    fig,axs=plt.subplots(rows,2,figsize=(6.4,2.18*rows),squeeze=False,layout='constrained')
    for ax,(d,m,tag) in zip(axs.flat,settings):
        vals=[idx[(d,m,tag,'single',method)] for method in methods]
        med=np.array([float(r['active_seconds']) for r in vals])
        low=np.array([float(r['active_seconds_min']) for r in vals])
        high=np.array([float(r['active_seconds_max']) for r in vals])
        x=np.arange(6)
        ax.bar(x,med,width=.65,color=colors,zorder=2)
        ax.errorbar(x,med,yerr=np.vstack([med-low,high-med]),fmt='none',ecolor='#222222',capsize=2,linewidth=1,zorder=3)
        ax.set_xticks(x,methods,rotation=30,ha='right')
        ax.set_ylabel('Active time (s)')
        ax.set_title(f"{'SIFT' if d=='sift' else 'GloVe'}, m={m}, gamma={'0.01' if tag=='01' else '0'}")
        ax.set_ylim(bottom=0)
        ax.grid(axis='y',color='#dddddd',linewidth=.5,zorder=0)
    for ext in ('pdf','png'):
        fig.savefig(ROOT/'figures'/f'{name}.{ext}',dpi=210)
    plt.close(fig)

plot_settings([(d,m,'01') for d in ('sift','glove') for m in (256,1024,4096)],'single-main',3)
plot_settings([(d,1024,'0') for d in ('sift','glove')],'single-negative',1)
print(json.dumps({'status':'PASS','source':'sealed aggregate.csv','new_experiments':False,'plots':['single-main','single-negative']}))
