"""Independently check scientific-review exports against archived coordinates and validation XML."""
import argparse,csv,gzip,hashlib,json
from pathlib import Path
from xml.etree import ElementTree as ET
import gemmi,numpy as np
ROOT=Path(__file__).resolve().parents[1]

def main(output=None):
    config=json.loads((ROOT/'build/config/scientific_review.json').read_text(encoding='utf-8'))
    source_config=json.loads((ROOT/'build/config/sources.json').read_text(encoding='utf-8'))
    structures=json.loads((ROOT/'build/config/structures.json').read_text(encoding='utf-8'))
    expected={(s['pdb'],p['number'],role):c['identity'] for s in structures for p in s['protomers'] for role,c in p['cofactors'].items()}
    actual={(r['pdb'],r['protomer'],r['role']):r['identity'] for r in config['cofactors']}
    assert actual==expected
    atoms={};validation={}
    for cid,src in source_config.items():
        raw=gzip.decompress((ROOT/'build'/src['file']).read_bytes())
        assert hashlib.sha256(raw).hexdigest()==src['sha256']==config['validation_sources'][cid]['coordinate_source_sha256']
        table=gemmi.cif.read_string(raw.decode('utf-8')).sole_block().get_mmcif_category('_atom_site.')
        records={};ranks={}
        for i in range(len(table['id'])):
            if str(table['pdbx_PDB_model_num'][i])!='1':continue
            ident=':'.join(str(table[k][i]) for k in ['label_comp_id','auth_asym_id','auth_seq_id','label_atom_id'])
            occ=float(table['occupancy'][i])
            if ident not in records or occ>ranks[ident]:
                records[ident]=np.array([float(table[k][i]) for k in ['Cartn_x','Cartn_y','Cartn_z']]);ranks[ident]=occ
        atoms[cid]=records
        v=config['validation_sources'][cid];blob=(ROOT/'build'/v['file']).read_bytes()
        assert hashlib.sha256(blob).hexdigest()==v['sha256']
        validation[cid]=ET.fromstring(gzip.decompress(blob))
    carbonyls=0
    for row in config['cofactors']:
        cid=row['pdb'];native=row['identity'];comp,ch,num=native.split(':')
        xyz=atoms[cid]
        for bond in row['carbonyl_bonds']:
            measured=float(np.linalg.norm(xyz[native+':'+bond['atoms'][0]]-xyz[native+':'+bond['atoms'][1]]))
            assert abs(measured-bond['distance_A'])<1e-7,(native,bond)
            carbonyls+=1
        if 'ring_atoms' in row:
            points=np.array([xyz[native+':'+n] for n in row['ring_atoms']]);center=points.mean(0)
            _,_,vh=np.linalg.svd(points-center);offset=(points-center)@vh[-1]
            assert abs(float(np.sqrt(np.mean(offset**2)))-row['ring_plane_RMS_A'])<1e-7
        groups=[e for e in validation[cid].iter('ModelledSubgroup') if (e.attrib.get('resname'),e.attrib.get('chain'),e.attrib.get('resnum'))==(comp,ch,num)]
        fresh=[dict(attributes=e.attrib,outliers=[dict(type=c.tag,**c.attrib) for c in e]) for e in groups]
        assert fresh==row['validation'],(native,'validation attributes/outliers differ')
    for pair in config['Mg_pairs']:
        measured=float(np.linalg.norm(atoms[pair['pdb']][pair['atom1']]-atoms[pair['pdb']][pair['atom2']]))
        assert abs(measured-pair['distance_A'])<1e-7
    exported=json.loads((ROOT/'downloads/validation/cofactor_geometry.json').read_text(encoding='utf-8'))
    assert exported==config
    with (ROOT/'downloads/validation/cofactor_geometry.csv').open(encoding='utf-8',newline='') as f:rows=list(csv.DictReader(f))
    assert len(rows)==len(expected)
    assert {(r['pdb'],int(r['protomer']),r['role']):r['identity'] for r in rows}==expected
    supplements=set(config['supplement_entries']);assert len(supplements)==8
    for scene in json.loads((ROOT/'build/config/scenes.json').read_text(encoding='utf-8')):
        if scene['pdb'] in ['1JB0','7DKZ','9KZ9'] and scene['part'] in ['A1A','A1B']:
            assert any('Source-geometry caution' in n for n in scene.get('notes',[])),scene['key']
    result=dict(status='PASS',entries=len(source_config),cofactor_roles=len(expected),carbonyl_bonds_checked=carbonyls,Mg_pairs_checked=len(config['Mg_pairs']),validation_XML_sources=len(validation),checks=['Coordinate/validation source hashes','Native carbonyl lengths and ring-planarity reproduction','Official per-ligand XML metrics and outliers','Export/config consistency','Critical A1 geometry caveat retention','Eight-entry supplement scope'])
    if output:Path(output).write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--json');main(p.parse_args().json)
