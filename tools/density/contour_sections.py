import copy,csv,json
from pathlib import Path
import numpy as np
from common import config,source as load_source
ARGS=config();R=ARGS.repo;N=ARGS.work_dir
import prepare as M
def main():
    assert ARGS.ids in (None,['9AU4']), 'This display supplement is only defined for 9AU4'
    pdb='9AU4';report=json.loads((N/'reports'/f'{pdb}_density_v02.json').read_text(encoding='utf-8'));source=load_source(pdb,ARGS)
    grid,diff,author,extent,info=M.grid_source(source);level=report['source']['full_grid_mean']+3*report['source']['full_grid_std'];assert author/report['source']['full_grid_std']<.25
    out=N/'previews_contour_supplement_v01'/pdb;out.mkdir(parents=True,exist_ok=True);rows=list(csv.DictReader((N/'reports'/f'{pdb}_atom_samples_v02.csv').open(encoding='utf-8')));scenes=[]
    for original in report['scenes']:
        key=original['scene'];sc=copy.deepcopy(M.js(R/'data/views'/(key+'.js'),'PSI_VIEWS['));lookup={r['atom']:[float(r[x]) for x in ['x','y','z']] for r in rows if r['scene']==key}
        for i,a in enumerate(sc['atoms']):a[3:6]=lookup[M.native_id(sc,i)]
        slices=[]
        for old in original['slices']:
            c=np.array(old['plane_center_A']);u=np.array(old['plane_u']);v=np.array(old['plane_v']);points=[c-u-v,c+u-v,c+2*v]
            slices.append(M.plot(sc,grid,None,level,extent,out,old['label'].replace(' ','_')+'_display_3SD',points,set(old['target_atoms']),'global 3-SD display'))
        scenes.append(dict(scene=key,slices=slices))
    note='9AU4 author contour 0.0149 is only about 0.015 times the full-grid SD and floods the local sections. Original author-level views are retained. Additional exploratory views use raw-map mean + 3 full-grid SD (and 0.8/1.0/1.2 times that level). This is a display sensitivity choice, not normalization, a quality score, uncertainty, or a support test.'
    (N/'reports/9AU4_contour_supplement_v01.json').write_text(json.dumps(dict(pdb=pdb,author_level=author,display_level=level,note=note,scenes=scenes),indent=2),encoding='utf-8')
    print('9AU4 exploratory sections generated; render meshes separately with --contour-mode mean-plus-3sd',flush=True)
if __name__=='__main__':main()
