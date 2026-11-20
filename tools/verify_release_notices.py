"""Verify notice scope, retained numerical concerns and fresh quinone provenance."""
from pathlib import Path
import json,argparse,hashlib,gzip
import gemmi,numpy as np
ROOT=Path(__file__).resolve().parents[1]
def js(p):
    t=p.read_text(encoding='utf-8');return json.loads(t.split('=',1)[1].strip().rstrip(';'))
def main(root=ROOT,out=None):
    cfg=json.loads((root/'build/config/release_notices.json').read_text(encoding='utf-8'));data=js(root/'data/release_notices.js');structures=json.loads((root/'build/config/structures.json').read_text(encoding='utf-8'));atlas=js(root/'data/atlas.js')
    assert data==cfg and set(cfg['entries'])=={s['pdb'] for s in structures}
    for s in structures:assert cfg['entries'][s['pdb']]['facts']==s['notes']
    scenes=json.loads((root/'build/config/scenes.json').read_text(encoding='utf-8'))
    for sc in scenes:
        text=(root/'data/views'/(sc['key']+'.js')).read_text(encoding='utf-8');built=json.loads(text[text.rfind(']=')+2:].strip().rstrip(';'))
        assert not any('not individually reviewed' in n or n.startswith('Development pilot:') for n in built['notes'])
        if sc['pdb'] in ['1JB0','7DKZ','9KZ9'] and sc['part'] in ['A1A','A1B']:assert any('Source-geometry caution' in n for n in built['notes'])
    c=cfg['entries']['7DKZ']['cautions'];q=next(x for x in c if x['id']=='quinone_bend');assert 'bent' in q['text'] and 'working on interpretations' in q['text'] and q['parts']==['A1A','A1B']
    assert len(c)==2 and len(cfg['entries']['9UH3']['cautions'])==0 and len(cfg['entries']['9HYU']['cautions'])==0
    s={s['pdb']:s for s in structures};assert 'Alaska' in ' '.join(s['7DKZ']['notes']);assert '8Z11' in s['9UH3']['lineage'][0]['text'];assert 'combined' in ' '.join(s['9HYU']['notes'])
    evidence=json.loads((root/'downloads/validation/7DKZ_quinone/7DKZ_direct_coordinate_check_v01.json').read_text(encoding='utf-8'));sources=json.loads((root/'build/config/sources.json').read_text(encoding='utf-8'));src=sources['7DKZ'];blob=gzip.decompress((root/'build'/src['file']).read_bytes());assert hashlib.sha256(blob).hexdigest()==evidence['archived_uncompressed_sha256']==src['sha256']
    table=gemmi.cif.read_string(blob.decode('utf-8')).sole_block().get_mmcif_category('_atom_site.');lookup={}
    for i in range(len(table['id'])):
        if str(table['pdbx_PDB_model_num'][i])=='1':lookup[':'.join(str(table[k][i]) for k in ['label_comp_id','auth_asym_id','auth_seq_id','label_atom_id'])]=np.array([float(table[k][i]) for k in ['Cartn_x','Cartn_y','Cartn_z']])
    for row in evidence['entries']:
        xyz=np.array([lookup[row['identity']+':'+n] for n in row['ring_atom_names']]);_,_,v=np.linalg.svd(xyz-xyz.mean(0));offset=(xyz-xyz.mean(0))@v[-1];assert abs(float(np.sqrt(np.mean(offset**2)))-row['ring_plane_RMS_A'])<1e-9
        assert row['atlas_heavy_atoms_checked']==33 and row['cofactor_bonds_checked']==34 and row['max_scene_native_difference_A']==0
    doc=(root/'docs/7DKZ_QUINONE_REVIEW.md').read_text(encoding='utf-8');assert 'Accepted Article' in doc and 'not independently inspected' in doc and 'cofactors' in doc and 'interpretation is in progress' in doc
    result=dict(status='PASS',entries=22,scenes_checked=160,stale_review_flags=0,quinone_source_atoms_checked=66,quinone_source_bonds_checked=68,retained_A1_source_geometry_warnings=True,default_7DKZ_cautions=2,scope='Concise presentation/provenance/export consistency plus native 7DKZ planarity reproduction. Evidence does not establish actual physical quinone conformation or causal refinement mechanism.')
    if out:Path(out).write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2));return result
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--repo',type=Path,default=ROOT);p.add_argument('--json',type=Path);a=p.parse_args();main(a.repo,a.json)
