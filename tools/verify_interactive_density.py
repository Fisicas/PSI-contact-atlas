"""Verify every native atom, grid payload, source/preset binding and fallback."""
from pathlib import Path
import argparse,base64,gzip,hashlib,json,math,struct
import gemmi,numpy as np
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def js(p):
 s=p.read_text(encoding='utf-8');return json.loads(s[s.rfind(']=')+2:].strip().rstrip(';')) if 'PSI_VIEWS' in s[:200] else json.loads(s.split('=',1)[1].strip().rstrip(';'))
def verify(R):
 A=js(R/'data/atlas.js');D=js(R/'data/density_review.js');I=js(R/'data/density_interactive_index.js');P=json.loads((R/'build/provenance/interactive_density_v01.json').read_text(encoding='utf-8'));assert I==json.loads((R/'build/config/interactive_density_index.json').read_text(encoding='utf-8'))
 assert set(I['scenes'])==set(D['scenes']) and len(I['scenes'])==160
 sources=json.loads((R/'build/config/sources.json').read_text(encoding='utf-8'));prepared={r['scene']:r for r in P['scenes']};scenes=maps=voxels=atoms=presets=0;protomers=set();unavailable=[]
 for structure in A['structures']:
  pdb=structure['pdb'];source=sources[pdb];raw=gzip.decompress((R/'build'/source['file']).read_bytes());assert hashlib.sha256(raw).hexdigest()==source['sha256'];tab=gemmi.cif.read_string(raw.decode()).sole_block().get_mmcif_category('_atom_site.');lookup={}
  for row in range(len(tab['id'])):
   if tab.get('pdbx_PDB_model_num',['1']*len(tab['id']))[row]!='1':continue
   k=':'.join(tab[c][row] for c in ['label_comp_id','auth_asym_id','auth_seq_id','label_atom_id']);lookup.setdefault(k,[]).append([float(tab[c][row]) for c in ['Cartn_x','Cartn_y','Cartn_z']])
  for prot in structure['protomers']:
   for view in prot['views']:
    key=view['key'];item=I['scenes'][key];assert (item['pdb'],item['protomer'],item['part'])==(pdb,prot['number'],view['part'])
    if item['status']=='unavailable':assert pdb=='1JB0' and not item['presets'] and 'payload' not in item;unavailable.append(key);continue
    payload_path=R/item['payload'];assert sha(payload_path)==item['payload_sha256']==prepared[key]['payload_sha256'];V=js(payload_path);S=V['scene'];original=js(R/'data/views'/f'{key}.js');assert S['key']==key and len(S['atoms'])==len(original['atoms']);assert S['contacts']==original['contacts'] and S['bonds']==original['bonds'] and S['residues']==original['residues']
    for a,b in zip(S['atoms'],original['atoms']):
     assert a[:3]==b[:3] and a[6:]==b[6:];r=S['residues'][a[2]];identity=':'.join([r['comp'],r['chain'],r['num'],a[0]]);assert any(max(abs(x-y) for x,y in zip(a[3:6],v))<1e-9 for v in lookup[identity]),(key,identity,'not native XYZ');atoms+=1
    for c in S['contacts']:assert abs(math.dist(S['atoms'][c['i']][3:6],S['atoms'][c['j']][3:6])-c['d'])<6e-6,(key,'distance')
    assert len(item['presets'])==len(D['scenes'][key]['meshes'])
    for i,(preset,im) in enumerate(zip(item['presets'],D['scenes'][key]['meshes'])):
     assert preset['id']==i and preset['image']==im['src'] and preset['label']==im['label'] and sha(R/im['src'])==preset['image_sha256'];assert preset['level']>0;presets+=1
    assert set(V['maps'])==({'primary','difference'} if V['method']=='X-ray' else {'primary'});assert V['units']==('full-cell σ' if V['method']=='X-ray' else 'raw EM units')
    for kind,rec in V['maps'].items():
     raw=base64.b64decode(rec['base64']);assert hashlib.sha256(raw).hexdigest()==rec['sha256']==prepared[key]['maps'][kind]['sha256'];assert raw[208:212]==b'MAP ';nx,ny,nz,mode=struct.unpack_from('<4i',raw);assert mode==2;offset=1024+struct.unpack_from('<i',raw,92)[0];vals=np.frombuffer(raw,dtype='<f4',offset=offset,count=nx*ny*nz).reshape((nz,ny,nx)).transpose(2,1,0);g=rec['grid'];assert list(vals.shape)==g['shape'];assert hashlib.sha256(vals.astype('<f4').ravel(order='C').tobytes()).hexdigest()==g['data_sha256'];assert rec['source_crop_roundtrip_error']<=rec['source_crop_allowed_roundtrip_error']
     cell=gemmi.UnitCell(*g['cell'])
     for sample in g['sample_checks']:
      ijk=sample['ijk'];value=vals[tuple(ijk)];assert (sample['value'] is None and np.isnan(value)) or float(value)==sample['value'];pos=cell.orthogonalize(gemmi.Fractional(*[(g['start'][i]+ijk[i])/g['intervals'][i] for i in range(3)]));assert max(abs(x-y) for x,y in zip(list(pos),sample['xyz_A']))<1e-9
     maps+=1;voxels+=vals.size
    for f in V['focus_indices']:assert 0<=f<len(S['atoms'])
    scenes+=1;protomers.add((pdb,prot['number']))
 assert scenes==156 and len(protomers)==39 and maps==172 and len(unavailable)==4 and presets==208
 assert {p.stem for p in (R/'data/density_interactive').glob('*.js')}==set(prepared)
 vendor=json.loads((R/'build/provenance/3dmol_vendor_v01.json').read_text(encoding='utf-8'))
 for file in ['3Dmol-min.js','LICENSE','package.json']:assert sha(R/'vendor/3dmol'/file)==vendor['files'][file]['sha256']
 return dict(status='PASS',available_scenes=scenes,available_protomers=len(protomers),unavailable_scenes=unavailable,map_payloads=maps,voxels=int(voxels),native_atoms=atoms,matched_static_presets=presets,source_coordinates_unchanged=True,contacts_and_bonds_unchanged=True,scope='Independent archived-source XYZ, distances, native crop bytes/voxel order/affine samples, source presets and static-image hashes. Real-browser/parser/interaction review is recorded separately; positive density does not validate chemistry.')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--repo',type=Path,default=ROOT);p.add_argument('--json',type=Path);a=p.parse_args();r=verify(a.repo)
 if a.json:a.json.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
 print(json.dumps(r,indent=2))
