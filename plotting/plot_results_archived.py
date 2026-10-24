"""Publication-style descriptive plots, generated only after native timing completes."""
import os
from config import HERE,load
os.environ['MPLCONFIGDIR']=str(HERE/'cache/matplotlib')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

COLORS={'complete':'#777777','batch':'#aaaaaa','merge':'#3977af','bits':'#61a66a','value':'#bd9847','frontier':'#c74a4a'}

def draw(ax,rows,title,field):
    vals=[r[field] for r in rows]
    errors=[[v-r[field+'_min'] for r,v in zip(rows,vals)],[r[field+'_max']-v for r,v in zip(rows,vals)]]
    ax.bar(range(len(rows)),vals,yerr=errors,capsize=3,color=[COLORS[r['mode']] for r in rows],width=.72)
    ax.set_xticks(range(len(rows)),[r['mode'] for r in rows],rotation=40,ha='right')
    ax.set_ylim(bottom=0);ax.set_title(title,fontsize=11);ax.set_ylabel('Seconds');ax.grid(axis='y',alpha=.2);ax.set_axisbelow(True)

def main():
    data=load(HERE/'RESULTS.json');assert data['status']=='PASS';rows=data['aggregate']
    order=list(COLORS)
    cases=[(d,nl,'01') for d in ('sift','glove') for nl in (256,1024,4096)]+[(d,1024,'0') for d in ('sift','glove')]
    fig,axes=plt.subplots(2,4,figsize=(16,7),layout='constrained')
    for ax,(d,nl,g) in zip(axes.flat,cases):
        rs=sorted([r for r in rows if (r['dataset'],r['nlist'],r['tag'],r['workload'])==(d,nl,g,'single')],key=lambda r:order.index(r['mode']))
        draw(ax,rs,f"{d.upper()} | nlist={nl} | gamma={'0.01' if g=='01' else '0'}",'active_seconds')
    fig.suptitle('Single-target calibration: median of 3 processes; bars show min-max (not confidence intervals)',fontsize=13)
    for ext in ('png','pdf'): fig.savefig(HERE/f'single-target.{ext}',dpi=180)
    plt.close(fig)
    fig,axes=plt.subplots(2,2,figsize=(10,8),layout='constrained')
    for ax,(w,d) in zip(axes.flat,[(w,d) for w in ('alpha4','mixed16') for d in ('sift','glove')]):
        rs=sorted([r for r in rows if (r['dataset'],r['workload'])==(d,w)],key=lambda r:order.index(r['mode']))
        draw(ax,rs,f'{d.upper()} | {w} | nlist=1024','active_seconds')
    fig.suptitle('Multiple targets with shared caches: initial generation included\nMedian of 3 processes; min-max (not confidence intervals)',fontsize=13)
    for ext in ('png','pdf'): fig.savefig(HERE/f'multiple-targets.{ext}',dpi=180)
    plt.close(fig)
    fig,axes=plt.subplots(1,2,figsize=(8,4),layout='constrained')
    for ax,d in zip(axes,('sift','glove')):
        rs=sorted([r for r in rows if (r['dataset'],r['workload'])==(d,'fresh')],key=lambda r:order.index(r['mode']))
        draw(ax,rs,f'{d.upper()} | existing index, fresh exact labels','joint_seconds')
    fig.suptitle('Joint measured input, labeling, warmup and calibration time\nMedian of 3 processes; min-max (not confidence intervals)',fontsize=12)
    for ext in ('png','pdf'): fig.savefig(HERE/f'fresh-label-joint.{ext}',dpi=180)
    plt.close(fig)
    print('PLOTS_COMPLETE single-target, multiple-targets, fresh-label-joint',flush=True)

if __name__=='__main__': main()
