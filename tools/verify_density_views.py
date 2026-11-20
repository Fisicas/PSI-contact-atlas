"""Validate optional density coverage, provenance, image identity and PNG integrity."""
import argparse,hashlib,json,struct,zlib
from pathlib import Path
R=Path(__file__).resolve().parents[1]
def js(path,prefix):
    t=path.read_text(encoding='utf-8');return json.loads(t[t.index('=',t.index(prefix))+1:].strip().rstrip(';'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def png(path):
    data=path.read_bytes();assert data[:8]==b'\x89PNG\r\n\x1a\n',path;pos=8;dimensions=None;ended=False
    while pos<len(data):
        length=struct.unpack('>I',data[pos:pos+4])[0];kind=data[pos+4:pos+8];body=data[pos+8:pos+8+length];crc=struct.unpack('>I',data[pos+8+length:pos+12+length])[0];assert zlib.crc32(kind+body)&0xffffffff==crc,(path,kind)
        if kind==b'IHDR':dimensions=struct.unpack('>II',body[:8]);assert dimensions[0]>=1000 and dimensions[1]>=800,(path,dimensions)
        pos+=12+length
        if kind==b'IEND':ended=True;break
    assert ended and pos==len(data),(path,'incomplete PNG');return dimensions
def main(output):
    atlas=js(R/'data/atlas.js','PSI_ATLAS');data=js(R/'data/density_review.js','PSI_DENSITY');prov=json.loads((R/'build/provenance/density_all_protomers_v01.json').read_text(encoding='utf-8'))
    expected={v['key']:(s['pdb'],p['number'],v['part']) for s in atlas['structures'] for p in s['protomers'] for v in p['views']}
    assert set(data['scenes'])==set(expected) and len(expected)==160
    assert set(data['entries'])=={s['pdb'] for s in atlas['structures']}
    for s in atlas['structures']:assert data['entries'][s['pdb']]['protomers']==[p['number'] for p in s['protomers']]
    figures={x['file']:x for x in prov['figures']};seen=set();available=0;unavailable=[];count=dict(sections=0,meshes=0)
    for key,(pdb,prot,part) in expected.items():
        item=data['scenes'][key];assert (item['protomer'],item['part'])==(prot,part)
        if item['status']=='unavailable':
            assert pdb=='1JB0' and not item['sections'] and not item['meshes'] and 'No released experimental data' in item['message'];unavailable.append(key);continue
        assert item['status']=='available' and item['sections'] and item['meshes'];available+=1
        for mode in count:
            for image in item[mode]:
                rel=image['src'];assert rel.startswith('media/density_all_protomers_v01/') and key in Path(rel).name,(key,rel)
                file=(R/rel).resolve();assert file.is_relative_to(R.resolve()) and file.is_file(),file
                record=figures[rel];assert record['scene']==key and record['sha256']==sha(file) and record['bytes']==file.stat().st_size
                if rel not in seen:png(file);seen.add(rel)
                count[mode]+=1
    assert len(unavailable)==4 and available==156 and seen==set(figures)
    assert sum(len(e['protomers']) for e in data['entries'].values())==40
    assert all(x['status']=='PASS' for x in prov['coordinate_frame_gate']['entries'])
    unavailable_source=next(x for x in prov['sources'] if x['pdb']=='1JB0');assert unavailable_source['rcsb_has_released_experimental_data']=='N'
    for source in prov['sources']:
        if source['status']!='available':continue
        for sc in source['scene_reports']:
            for crop in sc['crops'].values():assert crop['max_sampling_roundtrip_error']<crop['allowed_roundtrip_error']
            for plane in sc['slices']:assert plane['sample_spacing_A']==.14 and 0<=plane['source_coverage_fraction']<=1
        for sc in source['mesh_reports']+(source.get('contour_supplement') or {}).get('mesh_reports',[]):
            assert not sc['pymol_normalization_enabled'] and sc['carve_A']==2. and sc['buffer_A']==4.
            assert sc['Mg_atoms']==sc['Mg_spheres'] and sc['max_coordinate_change_A']==0
            for image in sc['images']:
                assert image['file'] in figures and image['sha256']==figures[image['file']]['sha256']
    assert prov['display_correction_20261120']['mesh_figures']==208
    for key in expected:
        text=(R/'downloads/pymol'/(key+'.pml')).read_text(encoding='utf-8')
        assert 'show spheres, lib_atoms and (elem MG or resn HOH)' in text
    result=dict(status='PASS',structures=22,protomers=40,scene_controls=len(expected),scenes_with_figures=available,unavailable_scenes=unavailable,unique_figures=len(seen),image_counts=count,checks=['Complete scene/protomer coverage','Native protomer identity in every asset path','Exact figure hashes and sizes','PNG chunk CRCs and dimensions','Explicit experimental-data unavailability','Coordinate-frame and crop-check records','Mesh processing settings, Mg visibility and unchanged coordinates'])
    if output:Path(output).write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(result,indent=2))
if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--json');main(a.parse_args().json)
