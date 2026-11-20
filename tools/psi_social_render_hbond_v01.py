"""Render only chemically compatible candidate guides, preserving every native atom."""
from pathlib import Path
import argparse,json,hashlib,os,shutil
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--repo',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
    R=a.repo.resolve();O=a.out.resolve();assert not O.exists();O.mkdir(parents=True)
    t=(R/'data/views/9EYS_prot1_P_A.js').read_text(encoding='utf-8');scene=json.loads(t[t.rfind(']=')+2:].strip().rstrip(';'))
    selected=[c for c in scene['contacts'] if c['cls'] in ['polar','water']]
    assert len(selected)==9 and sum(c['cls']=='polar' for c in selected)==4
    for c in selected:
        assert c['d']<=3.5
        assert ('donor–acceptor compatible' in c['basis']) if c['cls']=='polar' else ('water' in c['basis'])
    import pymol;pymol.finish_launching(['pymol','-cq']);from pymol import cmd
    os.chdir(R);cmd.do('@downloads/pymol/9EYS_prot1_P_A.pml');before=cmd.get_model('scene')
    for name in cmd.get_names('objects'):
        if cmd.get_type(name)=='object:measurement':cmd.delete(name)
    def sel(i):
        atom=scene['atoms'][i];res=scene['residues'][atom[2]]
        return f"scene and chain {res['chain']} and resi {res['num']} and resn {res['comp']} and name {atom[0]}"
    shown=[]
    cmd.set_color('social_polar',[0.09,0.541,0.235]);cmd.set_color('social_water',[0.043,0.498,0.612])
    for i,c in enumerate(selected,1):
        name=f'social_{c["cls"]}_{i:02}';measured=cmd.distance(name,sel(c['i']),sel(c['j']));assert abs(measured-c['d'])<1e-4
        cmd.set('dash_color','social_'+c['cls'],name);cmd.set('dash_length',.25,name);cmd.set('dash_gap',.18,name)
        shown.append(dict(object=name,contact_id=c['id'],class_key=c['cls'],chemical_basis=c['basis'],native_separation_A=c['d']))
    tail='scene and resn CL0 and name '+'+'.join(f'C{i}' for i in range(1,21))
    cmd.hide('everything',tail);cmd.hide('labels','all');cmd.set('dash_radius',.032);cmd.set('ray_opaque_background',0);cmd.set('ray_shadows',0);cmd.set('ambient',.5);cmd.set('specular',.2);cmd.set('antialias',2);cmd.set('valence',0)
    cmd.show('spheres','scene and elem MG');cmd.set('sphere_scale',.45,'scene and elem MG');cmd.turn('y',25);cmd.turn('x',-10);cmd.zoom('lib_atoms and not ('+tail+')',1.0,complete=1)
    cmd.png(str(O/'molecular_render_2200.png'),width=2200,height=2200,ray=1,quiet=1)
    after=cmd.get_model('scene');assert len(before.atom)==len(after.atom)==128
    assert all((x.chain,x.resi,x.resn,x.name,tuple(x.coord))==(y.chain,y.resi,y.resn,y.name,tuple(y.coord)) for x,y in zip(before.atom,after.atom))
    names=[n for n in cmd.get_names('objects') if cmd.get_type(n)=='object:measurement'];assert set(names)=={x['object'] for x in shown}
    report=dict(status='PASS',scene='9EYS_prot1_P_A',loaded_atoms=128,max_coordinate_change_A=0,displayed_measurement_guides=shown,omitted=[dict(contact_id=c['id'],class_key=c['cls'],basis=c['basis']) for c in scene['contacts'] if c['cls'] not in ['polar','water']],guides_are_candidates_not_confirmed_hydrogen_bonds=True,water_H_positions_protonation_angles_not_established=True,display_choices=['Phytyl atoms C1–C20 hidden, source atoms retained','All residue and distance labels hidden','All selected protein residues, cofactor core and water are retained in the full render','No acceptor–acceptor, intramolecular, packing or Mg–His measurement guides shown; Mg sphere and molecular topology retained','Orthographic camera/display only; no refinement or optimization'],source_sha256={rel:hashlib.sha256((R/rel).read_bytes()).hexdigest() for rel in ['data/views/9EYS_prot1_P_A.js','downloads/cif/9EYS_prot1_P_A.cif','downloads/pymol/9EYS_prot1_P_A.pml']},pymol_version=cmd.get_version(),camera=list(cmd.get_view()))
    (O/'native_contact_provenance_v01.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8');shutil.copy2(__file__,O/Path(__file__).name)
    print('PASS: 128 native atoms unchanged; exactly 4 polar and 5 water candidate guides.',flush=True);cmd.quit()
if __name__=='__main__':main()
