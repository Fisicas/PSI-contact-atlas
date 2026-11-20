"""Create full-precision figure-only scene CIFs from the archived native atom samples."""
import argparse,csv,hashlib,json
from pathlib import Path
import gemmi
from common import config,source as load_source,frame as bind_frame
ARGS=config();R=ARGS.repo;N=ARGS.work_dir

def main(pdb):
    rows=list(csv.DictReader((N/'reports'/(pdb+'_atom_samples_v02.csv')).open(encoding='utf-8')));keys=sorted({r['scene'] for r in rows});out=N/'native_scenes_v01';out.mkdir(exist_ok=True);checks=[]
    for key in keys:
        dest=out/(key+'.cif')
        lookup={r['atom']:[float(r[k]) for k in ['x','y','z']] for r in rows if r['scene']==key};doc=gemmi.cif.read_file(str(R/'downloads/cif'/(key+'.cif')));block=doc.sole_block();table=block.find('_atom_site.',['label_comp_id','auth_asym_id','auth_seq_id','label_atom_id','Cartn_x','Cartn_y','Cartn_z']);seen=set()
        for row in table:
            aid=':'.join(gemmi.cif.as_string(row[i]) for i in range(4));assert aid in lookup,aid
            for i,x in enumerate(lookup[aid]):row[4+i]=repr(x)
            seen.add(aid)
        assert seen==set(lookup)
        if not dest.exists():doc.write_file(str(dest))
        again=gemmi.cif.read_file(str(dest)).sole_block().find('_atom_site.',['label_comp_id','auth_asym_id','auth_seq_id','label_atom_id','Cartn_x','Cartn_y','Cartn_z']);error=max(max(abs(float(row[4+i])-lookup[':'.join(gemmi.cif.as_string(row[j]) for j in range(4))][i]) for i in range(3)) for row in again);assert error<1e-9
        checks.append(dict(scene=key,atoms=len(lookup),max_roundtrip_coordinate_error_A=error,file=str(dest),sha256=hashlib.sha256(dest.read_bytes()).hexdigest()))
    (N/'reports'/(pdb+'_native_cif_v01.json')).write_text(json.dumps(dict(pdb=pdb,scenes=checks,scope='Figure-only derivatives, full-precision positions from archived atlas sources. Original scene CIF/JS files unchanged.'),indent=2),encoding='utf-8')
if __name__=='__main__':
    atlas=json.loads((R/'data/atlas.js').read_text(encoding='utf-8').split('=',1)[1].strip().rstrip(';'))
    for s in atlas['structures']:
        if ARGS.ids and s['pdb'] not in ARGS.ids:continue
        report=N/'reports'/(s['pdb']+'_density_v02.json')
        if not report.exists():raise FileNotFoundError('Run prepare.py first: '+str(report))
        status=json.loads(report.read_text(encoding='utf-8'))['status']
        if status=='figures_generated':main(s['pdb'])
        elif status!='unavailable':raise ValueError('Incomplete preparation: '+str(report))
