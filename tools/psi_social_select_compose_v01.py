from pathlib import Path
import argparse,base64,json,hashlib,xml.etree.ElementTree as ET,http.server,threading,functools,sys,shutil
from PIL import Image
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--layout',type=Path,required=True);ap.add_argument('--render-dir',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--browser-runtime',type=Path,required=True);args=ap.parse_args()
    O=args.out.resolve();assert not O.exists();O.mkdir(parents=True)
    native=args.render_dir/'molecular_render_2200.png';prov=json.loads((args.render_dir/'native_contact_provenance_v01.json').read_text(encoding='utf-8'));assert prov['status']=='PASS' and len(prov['displayed_measurement_guides'])==9
    with Image.open(native) as im:
        bbox=im.getchannel('A').getbbox();assert bbox and bbox[0]>0 and bbox[1]>0 and bbox[2]<im.width and bbox[3]<im.height
    ns='http://www.w3.org/2000/svg';ET.register_namespace('',ns);root=ET.fromstring(args.layout.read_text(encoding='utf-8'));molecule=root.find(f'{{{ns}}}svg');assert molecule is not None
    molecule.set('viewBox',f'{bbox[0]-30} {bbox[1]-30} {bbox[2]-bbox[0]+60} {bbox[3]-bbox[1]+60}')
    molecule.find(f'{{{ns}}}image').set('href','data:image/png;base64,'+base64.b64encode(native.read_bytes()).decode())
    for node in root.findall(f'{{{ns}}}text'):
        if node.text=='9EYS · P_A environment':
            node.text='9EYS · P';sub=ET.SubElement(node,f'{{{ns}}}tspan',{'baseline-shift':'sub','font-size':'10'});sub.text='A';sub.tail=' environment'
    svg=O/'social-preview.svg';svg.write_text(ET.tostring(root,encoding='unicode'),encoding='utf-8');assert 'P_A' not in svg.read_text(encoding='utf-8')
    sys.path.insert(0,str(args.browser_runtime));from playwright.sync_api import sync_playwright
    class Handler(http.server.SimpleHTTPRequestHandler):
        def log_message(self,*args):pass
    server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(O)));threading.Thread(target=server.serve_forever,daemon=True).start();bounds=[]
    try:
        with sync_playwright() as pw:
            b=pw.chromium.launch(executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe',headless=True,args=['--disable-background-networking','--no-first-run'])
            for scale in [1,2]:
                c=b.new_context(viewport={'width':1280,'height':640},device_scale_factor=scale);c.route('**/*',lambda route:route.continue_() if route.request.url.startswith(('http://127.0.0.1:','data:')) else route.abort());page=c.new_page();page.goto(f'http://127.0.0.1:{server.server_port}/social-preview.svg')
                rects=page.evaluate('''()=>Array.from(document.querySelectorAll('svg>text')).map(e=>{let r=e.getBoundingClientRect();return {text:e.textContent,x:r.x,y:r.y,width:r.width,height:r.height}})''')
                for r in rects:
                    assert r['x']>=24 and r['y']>=24 and r['x']+r['width']<=1256 and r['y']+r['height']<=628,r
                    assert not(r['x']<1224 and r['x']+r['width']>626 and r['y']<586 and r['y']+r['height']>44),r
                assert page.locator('tspan[baseline-shift="sub"]').count()==1
                target=O/('social-preview.png' if scale==1 else 'social-preview-master-2560x1280.png');page.screenshot(path=str(target));assert scale==2 or target.stat().st_size<1_000_000
                bounds=rects;c.close()
            b.close()
    finally:server.shutdown();server.server_close()
    report=dict(status='PASS',selected_layout='Option 1 — editorial split; selected by user',canvas=[1280,640],master=[2560,1280],true_P_A_subscript=True,no_text_molecule_overlap=True,no_source_alpha_edge_clipping=True,native_alpha_bounds=bbox,text_bounds=bounds,render_provenance=prov,source_render_sha256=hashlib.sha256(native.read_bytes()).hexdigest(),source_layout_sha256=hashlib.sha256(args.layout.read_bytes()).hexdigest(),social_png_sha256=hashlib.sha256((O/'social-preview.png').read_bytes()).hexdigest(),social_png_bytes=(O/'social-preview.png').stat().st_size,scientific_scope='Only four donor–acceptor-compatible protein polar candidates plus five water-involved candidates are shown. No acceptor-pair/intramolecular/packing/Mg–His measurement guide. Molecular Mg and native atoms retained. This is a social-artwork choice only; atlas classes, selected contacts, default toggles and numerical data are unchanged. Hydrogen positions/angles/protonation and actual hydrogen bonds are not established.')
    (O/'composition_provenance_v01.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8');shutil.copy2(__file__,O/Path(__file__).name);print(json.dumps({'status':'PASS','folder':str(O),'bytes':report['social_png_bytes'],'guides':9,'true_subscript':True},indent=2))
if __name__=='__main__':main()
