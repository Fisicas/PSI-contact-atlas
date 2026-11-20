"""Package exact native density crops for lazy, offline interactive views."""
from pathlib import Path
import argparse,base64,copy,gzip,hashlib,json,re,sys
import gemmi,numpy as np
ROOT=Path(__file__).resolve().parents[1]
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
 return h.hexdigest()
def js(p):
 s=p.read_text(encoding='utf-8');return json.loads(s[s.rfind(']=')+2:].strip().rstrip(';')) if 'PSI_VIEWS' in s[:200] else json.loads(s.split('=',1)[1].strip().rstrip(';'))
def dump(p,x):p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def main(R,N):
 A=js(R/'data/atlas.js');D=js(R/'data/density_review.js');out=R/'data/density_interactive';assert not out.exists();out.mkdir()
 index=dict(version=1,scope='Development review; lazy native maps and unchanged static fallback images.',entries={},scenes={});report=dict(status='PASS',sources=[],scenes=[],map_count=0,voxel_count=0,payload_bytes=0)
 titles={'P_A':'P<sub>A</sub> network','special_pair':'Special pair','A1A':'A<sub>1A</sub> quinone','A1B':'A<sub>1B</sub> quinone'}
 for s in A['structures']:
  pdb=s['pdb'];entry=D['entries'][pdb];index['entries'][pdb]=dict(organism=s['organism'],condition=s['condition'],method=s['method'],source_url=entry.get('source_url',''),source_label=pdb+' experimental source',processing=entry.get('processing',''),summary=entry.get('summary',''))
  prep=json.loads((N/'reports'/f'{pdb}_density_v02.json').read_text(encoding='utf-8'))
  if prep['status']=='unavailable':
   for p in s['protomers']:
    for v in p['views']:index['scenes'][v['key']]=dict(pdb=pdb,protomer=p['number'],part=v['part'],title_html=titles[v['part']],status='unavailable',message=D['scenes'][v['key']]['message'],presets=[])
   continue
  source=prep['source'];source_file=Path(source['map_file']);assert source_file.exists() and sha(source_file)==source['map_sha256'],(pdb,'source hash')
  source_cfg=json.loads((R/'build/inputs/density_sources'/f'{pdb}.json').read_text(encoding='utf-8'));packaged=next(row for row in json.loads((R/'build/provenance/density_all_protomers_v01.json').read_text(encoding='utf-8'))['sources'] if row['pdb']==pdb)
  assert source['map_sha256']==packaged['source']['map_sha256'],(pdb,'prepared/packaged source mismatch')
  if source_cfg['records']:assert source['map_sha256'] in {r.get('sha256') for r in source_cfg['records']}
  else:assert source_cfg.get('reuse_previous_source') and source['map_sha256']==packaged['source']['map_sha256'],(pdb,'missing explicit reused-source binding')
  if source_cfg.get('emdb'):index['entries'][pdb]['source_label']=source_cfg['emdb']
  else:index['entries'][pdb]['source_label']=pdb+' deposited weighted map coefficients'
  xray=source['method']=='X-ray';units='full-cell σ' if xray else 'raw EM units';bykey={x['scene']:x for x in prep['scenes']}
  report['sources'].append(dict(pdb=pdb,sha256=source['map_sha256'],method=source['method'],normalization=source['normalization'],processing_source_sha256=sha(N/'reports'/f'{pdb}_density_v02.json')))
  for p in s['protomers']:
   for view in p['views']:
    key=view['key'];rec=bykey[key];sc=copy.deepcopy(js(R/'data/views'/f'{key}.js'));native=N/'native_scenes_v01'/f'{key}.cif';raw_cif=native.read_bytes();tab=gemmi.cif.read_string(raw_cif.decode()).sole_block().get_mmcif_category('_atom_site.')
    native_lookup={':'.join(tab[k][i] for k in ['label_comp_id','auth_asym_id','auth_seq_id','label_atom_id']):[float(tab[k][i]) for k in ['Cartn_x','Cartn_y','Cartn_z']] for i in range(len(tab['id']))};max_rounding=0
    for at in sc['atoms']:
     r=sc['residues'][at[2]];ident=':'.join([r['comp'],r['chain'],r['num'],at[0]]);xyz=native_lookup[ident];max_rounding=max(max_rounding,max(abs(a-b) for a,b in zip(at[3:6],xyz)));at[3:6]=xyz
    assert max_rounding<=.0011,(key,max_rounding)
    focus=[i for i,a in enumerate(sc['atoms']) if sc['residues'][a[2]].get('role') and ((sc['residues'][a[2]]['role'].startswith('A1') and (a[1]=='O' or a[0] in [f'C{j}' for j in range(1,11)])) or (not sc['residues'][a[2]]['role'].startswith('A1') and a[0] in ['OBD','O1D','O2D','O1A','O2A']))]
    if sc['part']=='P_A' and p.get('site_water'):
     water=p['site_water'].split(':');focus += [i for i,a in enumerate(sc['atoms']) if [sc['residues'][a[2]][k] for k in ['comp','chain','num']]==water[:3] and a[0]=='O']
    assert focus,key
    presets=[]
    for i,image in enumerate(D['scenes'][key]['meshes']):
     level=source['full_grid_mean']+3*source['full_grid_std'] if 'meshes_display_' in image['src'] else source['primary_level']
     if '_higher.png' in image['src']:level=1.5 if xray else 1.2*level
     presets.append(dict(id=i,image=image['src'],image_sha256=sha(R/image['src']),label=image['label'],caption=image['caption'],level=level,units=units,difference_levels=[3.,-3.] if xray else [],exploratory='meshes_display_' in image['src']))
    policy=json.loads((R/'build/config/release_notices.json').read_text(encoding='utf-8'))['entries'][pdb]
    cautions=[c['text'] for c in policy['cautions'] if (not c.get('parts') or sc['part'] in c['parts']) and (not c.get('protomers') or sc['protomer'] in c['protomers'])]
    missing=[r['role']+': '+p['cofactors'][r['role']]['atoms_note'] for r in sc['residues'] if r.get('role') and p['cofactors'].get(r['role'],{}).get('atoms_note')]
    payload=dict(scene=sc,native_cif=raw_cif.decode('utf-8'),focus_indices=sorted(set(focus)),method=source['method'],units=units,source_level=source['primary_level'],maps={},notes=list(dict.fromkeys(cautions+D['scenes'][key].get('feature_notes',[])+missing)))
    mapmeta={}
    for kind,c in rec['crops'].items():
     path=N/c['file'];raw=path.read_bytes();m=gemmi.read_ccp4_map(str(path));arr=np.array(m.grid,copy=True);shape=list(arr.shape);starts=[m.header_i32(i) for i in [5,6,7]];intervals=[m.header_i32(i) for i in [8,9,10]]
     assert [m.header_i32(i) for i in [17,18,19]]==[1,2,3] and [m.header_float(i) for i in [50,51,52]]==[0,0,0],(key,kind,'unsupported noncanonical header')
     assert not np.isinf(arr).any()
     def xyz(ijk):return list(m.grid.unit_cell.orthogonalize(gemmi.Fractional(*[(starts[k]+ijk[k])/intervals[k] for k in range(3)])))
     origin=xyz([0,0,0]);basis=[]
     for k in range(3):v=[0,0,0];v[k]=1;basis.append([a-b for a,b in zip(xyz(v),origin)])
     rng=np.random.default_rng(20261120);points={(x,y,z) for x in [0,shape[0]-1] for y in [0,shape[1]-1] for z in [0,shape[2]-1]};points|={tuple(int(rng.integers(0,n)) for n in shape) for _ in range(24)}
     grid=dict(shape=shape,start=starts,intervals=intervals,cell=list(m.grid.unit_cell.parameters),origin_A=origin,basis_A=basis,data_sha256=hashlib.sha256(arr.astype('<f4').ravel(order='C').tobytes()).hexdigest(),finite_voxels=int(np.isfinite(arr).sum()),nan_voxels=int(np.isnan(arr).sum()),sample_checks=[dict(ijk=list(v),xyz_A=xyz(v),value=float(arr[v]) if np.isfinite(arr[v]) else None) for v in sorted(points)])
     payload['maps'][kind]=dict(base64=base64.b64encode(raw).decode(),sha256=hashlib.sha256(raw).hexdigest(),grid=grid,source_crop_roundtrip_error=c['max_sampling_roundtrip_error'],source_crop_allowed_roundtrip_error=c['allowed_roundtrip_error'])
     assert c['max_sampling_roundtrip_error']<=c['allowed_roundtrip_error'];mapmeta[kind]={k:v for k,v in payload['maps'][kind].items() if k!='base64'};report['map_count']+=1;report['voxel_count']+=int(arr.size)
    target=out/f'{key}.js';target.write_text('window.PSI_DENSITY_PAYLOAD='+json.dumps(payload,separators=(',',':'),ensure_ascii=False)+';\n',encoding='utf-8');report['payload_bytes']+=target.stat().st_size
    index['scenes'][key]=dict(pdb=pdb,protomer=p['number'],part=view['part'],title_html=titles[view['part']],status='available',payload=target.relative_to(R).as_posix(),payload_bytes=target.stat().st_size,payload_sha256=sha(target),presets=presets)
    report['scenes'].append(dict(scene=key,atoms=len(sc['atoms']),native_cif_sha256=hashlib.sha256(raw_cif).hexdigest(),atlas_scene_sha256=sha(R/'data/views'/f'{key}.js'),max_original_scene_rounding_A=max_rounding,source_native_coordinates_changed=False,maps=mapmeta,payload_sha256=sha(target),preset_count=len(presets)))
  print(pdb,'packaged',flush=True)
 assert len(report['scenes'])==156 and report['map_count']==172 and len(index['scenes'])==160 and sum(len(x['presets']) for x in index['scenes'].values())==208
 (R/'data/density_interactive_index.js').write_text('window.PSI_DENSITY_INDEX='+json.dumps(index,separators=(',',':'),ensure_ascii=False)+';\n',encoding='utf-8')
 report.update(available_protomers=39,unavailable_protomers=1,scene_count=156,mesh_links=208,serialization='Original native CCP4 crop bytes embedded unchanged; model uses full-precision native crop XYZ. No additional normalization, smoothing, sharpening, resampling or refinement.',source_scope='Existing source-bound crop roundtrip checks retained; new browser parser/affine/value checks are separate. Raw full-map source files were freshly hash-checked; no source files overwritten.',qualification_policy='Source-specific scoped cautions and missing deposited cofactor-atom notes remain visible in the interactive view.')
 dump(R/'build/provenance/interactive_density_v01.json',report);dump(R/'build/config/interactive_density_index.json',index)
 print(json.dumps({k:report[k] for k in ['status','scene_count','map_count','voxel_count','payload_bytes','mesh_links']},indent=2))
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--repo',type=Path,default=ROOT);a.add_argument('--work-dir',type=Path,required=True);v=a.parse_args();main(v.repo,v.work_dir)
