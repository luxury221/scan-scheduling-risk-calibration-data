"""Draw a scheduling illustration; no empirical data or timings are added."""
from pathlib import Path
import os

ROOT = Path(__file__).resolve().parent
os.environ['MPLCONFIGDIR'] = str(ROOT / 'cache/matplotlib')
os.environ['TEMP'] = os.environ['TMP'] = str(ROOT / 'tmp')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 9,
                     'pdf.fonttype': 42, 'ps.fonttype': 42})
fig, axes = plt.subplots(1, 2, figsize=(7.0, 2.7))
for panel, (ax, title) in enumerate(zip(axes, [
        '(a) Positive-event initialization', '(b) Cluster-level initialization'])):
    ax.set_xlim(-0.8, 4.2)
    ax.set_ylim(-0.82, 2.45)
    ax.axis('off')
    ax.text(-0.65, 2.19, title, fontweight='bold', fontsize=9)
    for q, y, length in [('A', 1.25, 4), ('B', 0.33, 1)]:
        ax.text(-0.58, y + 0.25, f'{q}', fontweight='bold', va='center')
        for j in range(length):
            scanned = panel == 0 or j == 0
            fill = '#d7e7f2' if scanned else 'white'
            line = '#326486' if scanned else '#a9b0b8'
            ax.add_patch(FancyBboxPatch((j * 0.98, y), 0.82, 0.5,
                        boxstyle='round,pad=0.015,rounding_size=0.03',
                        facecolor=fill, edgecolor=line,
                        linestyle='solid' if scanned else 'dashed', linewidth=1))
            increment = '+h' if q == 'B' or j == 3 else '0'
            ax.text(j * 0.98 + 0.41, y + 0.27, increment, ha='center', va='center',
                    color='#1c425d' if scanned else '#8b939c')
            ax.text(j * 0.98 + 0.41, y - 0.14, f'list {j+1}',
                    ha='center', va='center', fontsize=7.5, color='#58616b')
    if panel == 0:
        ax.text(0, 1.96, 'Find A\'s first positive event', fontsize=8, color='#58616b')
    else:
        ax.text(0, 1.96, 'Expose A\'s first physical prefix', fontsize=8, color='#58616b')
    ax.text(0, -0.15, 'B\'s event is sufficient; its score is smaller', fontsize=7.7)
    ax.text(0, -0.54, 'Scanned before return: 5 lists' if panel == 0 else
            'Scanned before return: 2 lists', fontsize=8.5, fontweight='bold')
fig.subplots_adjust(left=0.035, right=0.99, top=0.98, bottom=0.12, wspace=0.16)
fig.text(0.5, 0.025, 'Illustrative local streams; dashed boxes are unscanned at return.',
         ha='center', fontsize=8, color='#58616b')
for ext in ['pdf', 'png']:
    fig.savefig(ROOT / 'figures' / f'lookahead-concept.{ext}', dpi=220)
plt.close(fig)
print('Created conceptual scheduling figure; no experiment data generated.')
