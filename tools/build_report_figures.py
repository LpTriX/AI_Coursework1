"""Draw report figures directly from the saved benchmark and mission files."""
from pathlib import Path
import json
import re
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Circle
from matplotlib.ticker import NullFormatter

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'reports/group38-latex/figures'
plt.rcParams.update({'font.size':11, 'font.family':'DejaVu Serif',
                     'axes.spines.top':False, 'axes.spines.right':False,
                     'pdf.fonttype':42, 'axes.labelsize':11,
                     'xtick.labelsize':11, 'ytick.labelsize':11})

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    datasets={k:json.loads((ROOT/'reference/part1b/results'/name).read_text())
              for k,name in [('MRV','benchmark.json'),('Row-major','benchmark_rowmajor.json')]}
    cases={order:{c['puzzle']:c for c in d['cases']} for order,d in datasets.items()}
    fig,axes=plt.subplots(1,2,figsize=(6.5,2.25))
    colors={'MRV':'#2363a1','Row-major':'#b45b25'}
    for ax,kind,title in zip(axes,['time','nodes'],['Solve time (ms)','Search calls']):
        for j,order in enumerate(['MRV','Row-major']):
            xs=[x+(-.13 if j==0 else .13) for x in [0,1]]
            med=[];low=[];high=[]
            for name in ['p1.txt','p2.txt']:
                runs=cases[order][name]['runs']
                vals=[r['elapsed_seconds']*1000 if kind=='time' else r['stats']['nodes'] for r in runs]
                v=sorted(vals)[len(vals)//2];med.append(v);low.append(v-min(vals));high.append(max(vals)-v)
            ax.errorbar(xs,med,yerr=[low,high],fmt='o' if j==0 else 's',
                        color=colors[order],capsize=3,markersize=6,label=order,lw=1.3)
        ax.set_yscale('log');ax.set_xticks([0,1],['p1','p2']);ax.set_xlim(-.5,1.5)
        ax.set_title(title,fontsize=11,pad=8)
        ax.grid(axis='y',which='major',color='#ddd',lw=.6)
        ax.yaxis.set_minor_formatter(NullFormatter())
    axes[0].set_ylim(.6,2000);axes[1].set_ylim(20,1e6)
    fig.legend(*axes[0].get_legend_handles_labels(),loc='lower center',ncol=2,
               frameon=False,bbox_to_anchor=(.5,-.02),fontsize=11)
    fig.subplots_adjust(left=.09,right=.99,top=.86,bottom=.29,wspace=.42)
    fig.savefig(OUT/'sudoku-ordering.pdf');plt.close(fig)

    mission=ROOT/'PDDL/PartA&B/mission2.pddl'
    edges=re.findall(r'\(connected (wp\d) (wp\d)\)',mission.read_text())
    assert len(edges)==9
    positions={'wp1':(0,0),'wp2':(1.8,0),'wp3':(3.6,0),
               'wp4':(0,1.35),'wp6':(1.8,1.35),'wp5':(3.6,1.35)}
    fig,ax=plt.subplots(figsize=(6.5,2.9));ax.set_aspect('equal');ax.axis('off')
    for a,b in edges:
        both=(b,a) in edges
        if both and a>b:continue
        ax.add_patch(FancyArrowPatch(positions[a],positions[b],
                     arrowstyle='<->' if both else '-|>',mutation_scale=13,
                     lw=1.5,color='#444',shrinkA=20,shrinkB=20))
    for n,(x,y) in positions.items():
        ax.add_patch(Circle((x,y),.22,fc='#eef3f8',ec='#2363a1',lw=1.4))
        ax.text(x,y,n.upper(),ha='center',va='center',fontsize=11)
    labels={n:[] for n in positions}
    for kind,source,lander in re.findall(r'\((image-saved|scan-saved|sample-stored) (wp\d) lander(\d)\)',mission.read_text()):
        label={'image-saved':'image','scan-saved':'scan','sample-stored':'sample'}[kind]
        labels[source].append(f'{label}: L{lander}')
    for lander,site in re.findall(r'\(lander-at lander(\d) (wp\d)\)',mission.read_text()):
        onboard=re.findall(r'\(aboard rover(\d) lander'+lander+r'\)',mission.read_text())
        deployed=re.findall(r'\(rover-at rover(\d) '+site+r'\)',mission.read_text())
        parts=[f'L{lander}']+[f'R{r} aboard' for r in onboard]+[f'R{r} deployed' for r in deployed]
        labels[site].insert(0,'; '.join(parts))
    labels={k:'\n'.join(v) for k,v in labels.items()}
    for n,(x,y) in positions.items():
        ax.text(x,y+(.40 if y else -.40),labels[n],ha='center',
                va='bottom' if y else 'top',fontsize=11,linespacing=1.25)
    ax.set_xlim(-.8,4.4);ax.set_ylim(-1.0,2.1)
    fig.subplots_adjust(left=0,right=1,top=1,bottom=0)
    fig.savefig(OUT/'mission2-map.pdf');plt.close(fig)
    print('Figures drawn from existing raw records; no benchmark data rewritten.')

if __name__=='__main__':main()
