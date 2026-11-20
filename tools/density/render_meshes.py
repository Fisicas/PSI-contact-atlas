"""Render optional fixed 3D meshes for every protomer with an available map source."""
import argparse,hashlib,json,os,subprocess,time
from pathlib import Path
import pymol
pymol.finish_launching(['pymol','-cq'])
from pymol import cmd
from common import config,source as load_source,frame as bind_frame
ARGS=config();R=ARGS.repo;N=ARGS.work_dir

def js(path,prefix='PSI_ATLAS'):
    t=path.read_text(encoding='utf-8');return json.loads(t[t.index('=',t.index(prefix))+1:].strip().rstrip(';'))
def render(s,prep):
    pdb=s['pdb'];out=ARGS.output_dir/'meshes'/pdb;out.mkdir(exist_ok=True,parents=True);assert all((N/'native_scenes_v01'/(s['scene']+'.cif')).exists() for s in prep['scenes']), 'Run native_cif.py before rendering'
    level=(prep['source']['full_grid_mean']+3*prep['source']['full_grid_std']) if ARGS.contour_mode=='mean-plus-3sd' else prep['source']['primary_level'];xray=prep['source']['method']=='X-ray';results=[]
    for record in prep['scenes']:
        key=record['scene'];sc=js(R/'data/views'/(key+'.js'),'PSI_VIEWS[');script=(R/'downloads/pymol'/(key+'.pml')).read_text(encoding='utf-8');native=N/'native_scenes_v01'/(key+'.cif');needle=f'load downloads/cif/{key}.cif, scene';assert needle in script;script=script.replace(needle,f'load "{native.as_posix()}", scene')
        cmd.reinitialize();cmd.do(script,flush=1,echo=0);assert cmd.count_atoms('lib_atoms')==len(sc['atoms']),(key,'native crop atom count')
        cmd.hide('labels','all')
        assert cmd.count_atoms('scene and elem MG and rep spheres')==cmd.count_atoms('scene and elem MG'), (key,'Mg sphere visibility')
        before_coords=[tuple(a.coord) for a in cmd.get_model('scene').atom]
        for name in cmd.get_names('objects'):
            if name.startswith('d') and name[1:3].isdigit():cmd.disable(name)
        expr=[]
        for r in sc['residues']:
            if not r.get('role'):continue
            atoms='(elem O or name C1+C2+C3+C4+C5+C6+C7+C8+C9+C10)' if r['role'].startswith('A1') else '(name OBD+O1D+O2D+O1A+O2A)'
            expr.append(f"(chain {r['chain']} and resi {r['num']} and resn {r['comp']} and {atoms})")
        prot=next(p for p in s['protomers'] if p['number']==sc['protomer']);water=prot.get('site_water')
        if water and sc['part']=='P_A':
            comp,ch,num,*atom=water.split(':');expr.append(f'(chain {ch} and resi {num} and resn {comp} and name O)')
        cmd.select('density_focus','scene and ('+' or '.join(expr)+')');assert cmd.count_atoms('density_focus')>0
        cmd.set('normalize_ccp4_maps',0);cmd.load(str(N/record['crops']['primary']['file']),'primary_map');cmd.set('mesh_width',.5);cmd.set('mesh_radius',.018)
        cmd.isomesh('main_mesh','primary_map',level,'density_focus',buffer=4.,carve=2.);cmd.color('marine','main_mesh')
        if xray:
            cmd.load(str(N/record['crops']['difference']['file']),'difference_map')
            for name,lev,col in [('positive_difference',3.,'green'),('negative_difference',-3.,'red')]:cmd.isomesh(name,'difference_map',lev,'density_focus',buffer=4.,carve=2.);cmd.color(col,name)
        cmd.zoom('density_focus',5.,complete=1);cmd.set('ray_shadows',0);cmd.set('ray_trace_mode',0);cmd.viewport(1100,825)
        images=[]
        for label,lev in [('primary',level)]+([('higher',1.5 if xray else 1.2*level)] if sc['part']=='P_A' and water else []):
            cmd.isolevel('main_mesh',lev);file=out/(key+('_higher' if label=='higher' else '')+'.png');cmd.png(str(file),1100,825,ray=1,quiet=1);assert file.exists() and file.stat().st_size>1000
            images.append(dict(file=str(file.relative_to(ARGS.output_dir)),level=lev,units='full-cell sigma' if xray else 'raw deposited EM units',kind=label,sha256=hashlib.sha256(file.read_bytes()).hexdigest()))
        results.append(dict(scene=key,protomer=sc['protomer'],part=sc['part'],images=images,carve_A=2.,buffer_A=4.,pymol_normalization_enabled=bool(cmd.get_setting_int('normalize_ccp4_maps')),native_atom_count=cmd.count_atoms('scene'),focus_atom_count=cmd.count_atoms('density_focus'),Mg_atoms=cmd.count_atoms('scene and elem MG'),Mg_spheres=cmd.count_atoms('scene and elem MG and rep spheres'),max_coordinate_change_A=max(abs(x-y) for a,b in zip(before_coords,[tuple(a.coord) for a in cmd.get_model('scene').atom]) for x,y in zip(a,b)),contour_mode=ARGS.contour_mode));assert not results[-1]['pymol_normalization_enabled']
        print(json.dumps(dict(mesh_scene=key,images=len(images))),flush=True)
    (ARGS.output_dir/'reports'/(pdb+'_meshes_v01.json')).write_text(json.dumps(dict(pdb=pdb,status='figures_generated',scenes=results,pymol_version=cmd.get_version()[0],scope='Fixed native-coordinate figures with display-only carve; not independent model support or an omit-map test.'),indent=2),encoding='utf-8')
def main(ids,watch):
    os.chdir(R);pending=[s for s in js(R/'data/atlas.js')['structures'] if not ids or s['pdb'] in ids]
    while pending:
        progressed=False
        for s in list(pending):
            pdb=s['pdb']
            if (ARGS.output_dir/'reports'/(pdb+'_meshes_v01.json')).exists():pending.remove(s);continue
            try:prep=json.loads((N/'reports'/(pdb+'_density_v02.json')).read_text(encoding='utf-8'))
            except (FileNotFoundError,json.JSONDecodeError):continue
            if prep['status']=='unavailable':pending.remove(s);progressed=True;continue
            render(s,prep);pending.remove(s);progressed=True
        if not watch:break
        if pending and not progressed:time.sleep(5)
    print(json.dumps(dict(remaining=[s['pdb'] for s in pending])),flush=True)
    if pending:raise RuntimeError('Requested entries lack preparation reports')
if __name__=='__main__':main(ARGS.ids,ARGS.watch)
