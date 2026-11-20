from pathlib import Path
import json,hashlib,shutil
import numpy as np,gemmi
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
import argparse
parser=argparse.ArgumentParser();parser.add_argument('--repo',type=Path,default=Path(__file__).resolve().parents[1]);parser.add_argument('--output-dir',type=Path,required=True);args=parser.parse_args()
R=args.repo;Q=args.output_dir;Q.mkdir(parents=True,exist_ok=True)
j=json.loads((R/'downloads/validation/7DKZ_quinone/7DKZ_direct_coordinate_check_v02.json').read_text(encoding='utf-8'))
names=['C'+str(i) for i in range(1,11)]+['O1','O4'];ccd=gemmi.cif.read_file(str(R/'build/inputs/ccd/PQN.cif')).sole_block();bonds=[(gemmi.cif.as_string(x[0]),gemmi.cif.as_string(x[1])) for x in ccd.find('_chem_comp_bond.',['atom_id_1','atom_id_2']) if gemmi.cif.as_string(x[0]) in names and gemmi.cif.as_string(x[1]) in names]
rows=[j['entries'][1],next(r for r in j['parent_geometry_context'] if r['identity']=='PQN:B:842'),j['CCD_ideal_geometry_context']]
titles=['7DKZ · PQN B843','4XK8 · PQN B842 (current record)','PQN CCD ideal geometry']
fig,axes=plt.subplots(2,3,figsize=(14,8.2));fig.subplots_adjust(left=.05,right=.99,top=.81,bottom=.17,hspace=.31,wspace=.23)
for col,(row,title) in enumerate(zip(rows,titles)):
    xyz=np.array([row['selected_atoms'][n]['xyz_A'] for n in names]);ring=xyz[:10];center=ring.mean(0);_,_,vh=np.linalg.svd(ring-center);basis=vh.T
    if np.linalg.det(basis)<0:basis[:,2]*=-1
    local=(xyz-center)@basis
    if local[names.index('O1'),0]>0:local[:,[0,2]]*=-1
    if local[names.index('O1'),1]<0:local[:,1:]*=-1
    for plane,dims in [(0,(0,1)),(1,(0,2))]:
        ax=axes[plane,col]
        for a,b in bonds:
            ii,jj=names.index(a),names.index(b);ax.plot(local[[ii,jj],dims[0]],local[[ii,jj],dims[1]],color='#71818d',lw=2.8,zorder=1)
        for idx,n in enumerate(names):
            ax.scatter(local[idx,dims[0]],local[idx,dims[1]],c='#d52932' if n.startswith('O') else '#5a6670',s=54,edgecolors='white',zorder=3)
            if plane==0 and n in ['C1','C2','C3','C4','O1','O4']:ax.annotate(n,local[idx,list(dims)],xytext=(4,7),textcoords='offset points',fontsize=9)
        ax.set_aspect('equal');ax.set_xlim(-4,4);ax.set_ylim((-3.5,3.5) if plane==0 else (-1.5,1.5));ax.set_xlabel('Local plane axis (Å)',fontsize=9);ax.tick_params(labelsize=8);ax.spines[['top','right']].set_visible(False)
        if plane==0:ax.set_title(title+'\nC–O '+f"{row['carbonyl_C1_O1_A']:.3f}, {row['carbonyl_C4_O4_A']:.3f} Å",fontsize=11,color='#10344e')
        else:ax.axhline(0,color='#b4c0c7',lw=.7,zorder=0);ax.set_title(f"Ring plane RMS {row['ring_plane_RMS_A']:.3f} Å; max |offset| {row['ring_max_abs_plane_A']:.3f} Å",fontsize=9)
axes[0,0].set_ylabel('View toward ring plane (Å)',fontsize=9);axes[1,0].set_ylabel('Out-of-plane displacement (Å)',fontsize=9)
fig.suptitle('The 7DKZ quinone bend is in the deposited coordinates',x=.05,ha='left',fontsize=20,fontweight='bold',color='#10344e')
fig.text(.05,.87,'All 33 atlas A1B atoms and 34 bonds match the fresh 7DKZ file / CCD connectivity. No coordinate correction was applied.',fontsize=11)
fig.text(.05,.09,'Ring carbons and two oxygen atoms only; flexible side chain omitted. Each panel is centered and rotated independently for display.\nPlane fits use ten ring carbons; coordinates are not moved onto a plane, optimized or refined. Connections show CCD topology, not bond orders.\nThe paper used 4XK8 with cofactors removed; current 4XK8 quinones are comparison references, not evidence of transferred ligands.\nThe source-model match proves faithful reproduction, not a physically validated native quinone conformation.',fontsize=9,color='#345267')
out=Q/'7DKZ_quinone_coordinate_comparison_v05.png';fig.savefig(out,dpi=160);fig.savefig(Q/'7DKZ_quinone_coordinate_comparison_v05.pdf');plt.close(fig)
print(out)
