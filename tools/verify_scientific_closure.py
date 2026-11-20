"""Check scientific closure scope, native axial distances and diagnostic exports.

Optional --map-cache directly resamples the six entries carrying focused local
qualifications. It requires hash-bound original maps and never fetches sources.
"""
from pathlib import Path
import argparse,csv,gzip,hashlib,json,math,sys
import gemmi,numpy as np
def run(repo,output=None,map_cache=None,work_dir=None):
    cfg=json.loads((repo/'build/config/scientific_review.json').read_text(encoding='utf-8'))
    text=(repo/'data/density_review.js').read_text(encoding='utf-8');density=json.loads(text.split('=',1)[1].strip().rstrip(';'))
    text=(repo/'data/atlas.js').read_text(encoding='utf-8');atlas=json.loads(text.split('=',1)[1].strip().rstrip(';'));structures={s['pdb']:s for s in atlas['structures']}
    reviewed={cid for cid,e in density['entries'].items() if e.get('reviewed')}
    assert reviewed==set(cfg['entries'])==set(structures)-{'1JB0'}
    assert sum(len(cfg['entries'][cid]['protomers_screened']) for cid in reviewed)==39
    assert sum(e['source_figures_inspected'] for e in cfg['entries'].values())==462
    sheets=json.loads((repo/'build/provenance/scientific_closure/baseline_figure_review.json').read_text(encoding='utf-8'))['sheets'];assert len(sheets)==48
    seen={}
    for sh in sheets:
        for fig in sh['figures']:seen[fig['src']]=fig['sha256']
    assert len(seen)==260
    for rel,sha in seen.items():assert hashlib.sha256((repo/rel).read_bytes()).hexdigest()==sha
    sources=json.loads((repo/'build/config/sources.json').read_text(encoding='utf-8'));atoms={}
    for cid,source in sources.items():
        raw=gzip.decompress((repo/'build'/source['file']).read_bytes());assert hashlib.sha256(raw).hexdigest()==source['sha256']
        table=gemmi.cif.read_string(raw.decode('utf-8')).sole_block().get_mmcif_category('_atom_site.');lookup={};rank={}
        for i in range(len(table['id'])):
            if str(table['pdbx_PDB_model_num'][i])!='1':continue
            ident=':'.join(str(table[k][i]) for k in ['label_comp_id','auth_asym_id','auth_seq_id','label_atom_id']);alt=table['label_alt_id'][i];r=(float(table['occupancy'][i]),alt in [None,False,'.','?'],str(alt)=='A')
            if ident not in lookup or r>rank[ident]:lookup[ident]=np.array([float(table[k][i]) for k in ['Cartn_x','Cartn_y','Cartn_z']]);rank[ident]=r
        atoms[cid]=lookup
    pairs=0
    for row in cfg['axial_geometry_review']['entries']:
        native=atoms[row['pdb']];assert row['source_sha256']==sources[row['pdb']]['sha256']
        for name,measure in row['distances'].items():
            d=float(np.linalg.norm(native[row['Mg']]-native[row['histidine']+':'+name]));assert abs(d-measure['distance_A'])<1e-9;pairs+=1
    rows=list(csv.DictReader((repo/'downloads/validation/diagnostic_density_samples.csv').open(encoding='utf-8')));expected=cfg['diagnostic_density_samples'];assert len(rows)==len(expected)==388
    assert sum(r['role']=='site_water' for r in rows)==37
    assert len({(r['scene'],r['atom']) for r in rows})==388
    for a,b in zip(rows,expected):
        for key,value in b.items():assert str(value)==a[key],(key,value,a[key])
        assert b['atom'] in atoms[b['pdb']] and b['coordinate_source_sha256']==sources[b['pdb']]['sha256']
        assert all(math.isfinite(b[k]) for k in ['primary_value','reference_level','value_over_display_level']) and b['reference_level']>0
        assert abs(b['primary_value']/b['reference_level']-b['value_over_display_level'])<1e-12
        prot=next(p for p in structures[b['pdb']]['protomers'] if p['number']==b['protomer'])
        assert b['atom']==prot['site_water'] if b['role']=='site_water' else b['atom'].startswith(prot['cofactors'][b['role']]['identity']+':')
    for cid in ['7COY','9S6P','9SK3','5OY0']:
        assert cfg['entries'][cid]['disposition'].startswith('RETAIN_WITH')
    assert 'weak' in cfg['entries']['9SK3']['density'].lower()
    assert 'unsharpened and unmasked' in cfg['entries']['9AU4']['density']
    scenes=json.loads((repo/'build/config/scenes.json').read_text(encoding='utf-8'))
    checks=0
    for sc in scenes:
        tag='Local-density qualification:' if sc['pdb']=='7COY' and sc['part'] in ['A1A','special_pair'] else 'Site-water qualification:' if sc['pdb'] in ['9S6P','9SK3'] and sc['part'] in ['P_A','special_pair'] else 'Axial-geometry qualification:' if sc['pdb']=='5OY0' and sc['protomer']==3 and sc['part'] in ['P_A','special_pair'] else None
        if tag:assert any(tag in n for n in sc.get('notes',[]));checks+=1
    direct=0;maxerror=0.
    if map_cache:
        assert work_dir,'--work-dir outside the repository is required for map checks'
        sys.path.insert(0,str(repo/'tools/density'));sys.argv=[__file__,'--repo',str(repo),'--work-dir',str(work_dir),'--map-cache',str(map_cache)]
        import prepare as M
        from common import source
        for cid in ['5OY0','7COY','7DKZ','9KZ9','9S6P','9SK3']:
            grid,diff,level,extent,info=M.grid_source(source(cid,M.ARGS));selected=[r for r in expected if r['pdb']==cid];xyz=np.array([atoms[cid][r['atom']] for r in selected]);values,inside=M.sample(grid,xyz,extent);assert inside.all()
            for row,value in zip(selected,values):
                err=abs(float(value)-row['primary_value']);maxerror=max(maxerror,err);assert err<1e-6 and abs(level-row['reference_level'])<1e-10;direct+=1
            del grid,diff
    result=dict(status='PASS',reviewed_entries=21,reviewed_protomers=39,packaged_figures_scope=462,additional_baseline_figure_hashes_checked=len(seen),native_axial_distances_checked=pairs,diagnostic_points_checked=388,water_points=37,scene_warning_checks=checks,direct_native_map_samples_checked=direct,max_direct_sampling_difference=maxerror,limitations='Scoped review and record consistency only. No hydrogen-bond, occupancy, redox, atom-fit, normal-coordination or biological-replication approval. Map ratios are source-specific display context.')
    if output:output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2));return result
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--repo',type=Path,default=Path(__file__).resolve().parents[1]);p.add_argument('--json',type=Path);p.add_argument('--map-cache',type=Path);p.add_argument('--work-dir',type=Path);a=p.parse_args();run(a.repo,a.json,a.map_cache,a.work_dir)
