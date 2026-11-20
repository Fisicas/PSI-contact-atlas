"""Check source-bound candidate-only social artwork without changing atlas data."""
from pathlib import Path
import argparse,json,hashlib,struct,base64,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def verify(root):
    report=json.loads((root/'build/provenance/branding/social_composition_v02.json').read_text(encoding='utf-8'))
    native=json.loads((root/'build/provenance/branding/social_native_contacts_v02.json').read_text(encoding='utf-8'))
    assert report['status']==native['status']=='PASS' and report['render_provenance']==native
    assert native['loaded_atoms']==128 and native['max_coordinate_change_A']==0
    for path,digest in native['source_sha256'].items():assert sha(root/path)==digest,path
    text=(root/'data/views/9EYS_prot1_P_A.js').read_text(encoding='utf-8');scene=json.loads(text[text.rfind(']=')+2:].strip().rstrip(';'))
    byid={c['id']:c for c in scene['contacts']};expected={c['id'] for c in scene['contacts'] if c['cls'] in ['polar','water']}
    actual=native['displayed_measurement_guides'];assert {c['contact_id'] for c in actual}==expected and len(actual)==9
    assert sum(c['class_key']=='polar' for c in actual)==4 and sum(c['class_key']=='water' for c in actual)==5
    for item in actual:
        c=byid[item['contact_id']];assert c['cls']==item['class_key'] and c['d']==item['native_separation_A'] and c['basis']==item['chemical_basis'] and c['d']<=3.5
        assert c['cls']=='water' or c['basis']=='donor–acceptor compatible'
    png=root/'media/branding/social-preview.png';raw=png.read_bytes();assert raw[:8]==b'\x89PNG\r\n\x1a\n' and struct.unpack('>II',raw[16:24])==(1280,640)
    assert len(raw)<1_000_000 and sha(png)==report['social_png_sha256'] and len(raw)==report['social_png_bytes']
    full=root/'media/branding/social-native-candidates.png';assert sha(full)==report['source_render_sha256']
    ns={'s':'http://www.w3.org/2000/svg'};svg=ET.parse(root/'media/branding/social-preview.svg').getroot();assert any(e.text=='A' and e.attrib.get('baseline-shift')=='sub' for e in svg.findall('.//s:tspan',ns))
    assert not any('P_A' in ''.join(e.itertext()) for e in svg.findall('.//s:text',ns))
    molecule=svg.find('s:svg',ns);assert molecule is not None;embedded=molecule.find('s:image',ns).attrib['href'];assert base64.b64decode(embedded.split(',',1)[1])==full.read_bytes()
    assert report['no_text_molecule_overlap'] and report['no_source_alpha_edge_clipping']
    return dict(status='PASS',scene=scene['key'],polar_candidate_guides=4,water_candidate_guides=5,non_Hbond_measurement_guides=0,native_atoms=128,max_coordinate_change_A=0,true_subscript=True,dimensions=[1280,640],bytes=len(raw),scope='Source IDs/classes/separations and image/SVG hashes checked against packaged scene/render records. Atlas classifications remain intact. Candidate chemistry does not establish hydrogen positions, angles or confirmed hydrogen bonds; raster interpretation relies on the documented native render and visual review.')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--repo',type=Path,default=ROOT);p.add_argument('--json',type=Path);a=p.parse_args();r=verify(a.repo)
    if a.json:a.json.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(r,indent=2))
