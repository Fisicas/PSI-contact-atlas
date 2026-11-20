from pathlib import Path
import sys,json,threading,http.server,functools,traceback,hashlib,time,argparse
from urllib.parse import urlparse,unquote
from PIL import Image
parser=argparse.ArgumentParser(description="Review a local PSI atlas in a fresh headless browser; never attaches to a personal browser.")
parser.add_argument('--repo',type=Path,default=Path(__file__).resolve().parents[1]);parser.add_argument('--work-dir',type=Path,required=True)
parser.add_argument('--runtime',type=Path,help='Optional separate pip --target package directory');parser.add_argument('--executable',type=Path)
parser.add_argument('--out',default='run_v01');parser.add_argument('--engine',default='chrome',choices=['chrome','edge']);parser.add_argument('--smoke',action='store_true');a=parser.parse_args()
R=a.repo.resolve();B=a.work_dir.resolve()
if B==R or R in B.parents:parser.error('Keep browser reports/runtime outside the repository')
B.mkdir(exist_ok=True,parents=True)
if a.runtime:sys.path.insert(0,str(a.runtime.resolve()))
from playwright.sync_api import sync_playwright
O=B/a.out;O.mkdir(exist_ok=False);(O/'screenshots').mkdir();(O/'downloads').mkdir()
class Handler(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*args):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(R)));threading.Thread(target=server.serve_forever,daemon=True).start()
http=f'http://127.0.0.1:{server.server_port}/index.html?still=1';file=R.joinpath('index.html').as_uri()+'?still=1'
def js(p):
    s=p.read_text(encoding='utf-8');return json.loads(s[s.index('=')+1:].strip().rstrip(';'))
atlas=js(R/'data/atlas.js');density=js(R/'data/density_review.js');scene_keys=[v['key'] for s in atlas['structures'] for p in s['protomers'] for v in p['views']]
additions=['9SE6','9LUT','8WEY','7DKZ','9UH3','9HYU','9KZ9','8XLS']
result=dict(status='RUNNING',engine=a.engine,started_UTC=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),isolation='Fresh chromium.launch(headless=True) and nonpersistent browser contexts. No personal profile, existing browser connection, external website, or published atlas used.',scenes=[],exports=[],downloads=[],comparisons=[],layouts=[],interactions=[],issues=[],errors=[],request_failures=[],blocked_external=[],screenshots=[])
page_contexts=[]
def save():
    (O/'browser_review_v01.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def shot(page,name,canvas=False):
    dest=O/'screenshots'/(name+'.png')
    (page.locator('#stage canvas') if canvas else page).screenshot(path=str(dest),**({} if canvas else {'full_page':True}))
    result['screenshots'].append(dest.relative_to(O).as_posix())
def capture_context(browser,mode):
    context=browser.new_context(viewport={'width':1440,'height':1100},device_scale_factor=1,accept_downloads=True,color_scheme='light')
    def restrict(route):
        if route.request.url.startswith(('http://127.0.0.1:','file:','blob:','data:')):route.continue_()
        else:result['blocked_external'].append(route.request.url);route.abort()
    context.route('**/*',restrict)
    assert not context.cookies() and not context.storage_state()['origins']
    context.add_init_script("""(() => { const native=CanvasRenderingContext2D.prototype.fillText;
      window.__psiText=[]; CanvasRenderingContext2D.prototype.fillText=function(text,x,y,...args){
        const m=this.measureText(String(text)), t=this.getTransform(); const caption=String(text).includes('PSI Contact Atlas') || (!this.canvas.isConnected && t.a===1 && t.d===1 && y>this.canvas.height*.88);
        if(window.__psiText.length<1500 || caption) window.__psiText.push({text:String(text),x,y,width:m.width,canvasW:this.canvas.width,canvasH:this.canvas.height,font:this.font,connected:this.canvas.isConnected,caption});
        return native.call(this,text,x,y,...args);
      }; })();""")
    page=context.new_page();requests=[]
    page.on('pageerror',lambda e:result['errors'].append(dict(mode=mode,url=page.url,type='pageerror',message=str(e))))
    page.on('console',lambda e:result['errors'].append(dict(mode=mode,url=page.url,type='console',message=e.text)) if e.type=='error' else None)
    page.on('requestfailed',lambda r:result['request_failures'].append(dict(mode=mode,url=r.url,error=r.failure)))
    page.on('request',lambda r:requests.append(r.url))
    page_contexts.append(context)
    return page,requests
def scene(page,base,key):
    page.evaluate('window.__psiText=[]')
    page.goto(base+'#/view/'+key)
    page.wait_for_function("""key => { const s=window.PSI_VIEWS?.[key],cv=document.querySelector('#stage canvas');
      return s&&cv&&cv.getAttribute('aria-label')===`${s.pdb} protomer ${s.protomer} ${s.part.replace('_',' ')}: ${s.atoms.length} deposited heavy atoms and ${s.contacts.length} measured separations. The table lists every value.` && document.querySelectorAll('#ctable tr[data-i]').length===s.contacts.length&&document.querySelector('#scale-note').textContent.includes('px/Å'); }""",arg=key)
    page.wait_for_function("document.querySelector('#stage canvas').width>0")
def images_ready(page):
    page.wait_for_function("document.querySelector('.density-content')?.innerHTML.length>0 && [...document.querySelectorAll('.density-figures img')].every(x=>x.complete&&x.naturalWidth>0)")
def download(page,selector,tag,expected=None):
    with page.expect_download(timeout=60000) as pending:page.locator(selector).click()
    d=pending.value;assert d.failure() is None,d.failure();dest=O/'downloads'/(tag+'__'+d.suggested_filename);d.save_as(dest)
    data=dest.read_bytes();assert data
    info=dict(tag=tag,file=dest.relative_to(O).as_posix(),suggested_filename=d.suggested_filename,bytes=len(data),sha256=hashlib.sha256(data).hexdigest())
    if expected:
        assert data==expected.read_bytes(),(tag,expected);info['byte_equal_to_repository']=expected.relative_to(R).as_posix()
    return info,dest
try:
    with sync_playwright() as p:
        exe=r'C:\Program Files\Google\Chrome\Application\chrome.exe' if a.engine=='chrome' else r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
        if a.executable:exe=str(a.executable)
        browser=p.chromium.launch(executable_path=exe,headless=True,args=['--disable-background-networking','--disable-component-update','--no-first-run','--no-default-browser-check'])
        result['browser_version']=browser.version;result['executable']=exe
        page,requests=capture_context(browser,'http')
        page.goto(http+'#/');page.wait_for_selector('#hero-host canvas')
        assert page.locator('.stats dd').all_text_contents()[:3]==['22','40','160']
        assert page.locator('.brand img').evaluate('(x)=>x.complete&&x.naturalWidth>0')
        page.keyboard.press('Tab');shot(page,'home_desktop_light')
        page.locator('#q').fill('9KZ9');assert '9KZ9' in page.locator('#structures').inner_text();page.locator('#q').fill('')
        keys=scene_keys if not a.smoke else ['9LUT_prot1_special_pair','9KZ9_prot1_P_A','7DKZ_prot1_A1A','1JB0_prot1_A1B','9AU4_prot3_P_A','9HYU_prot1_A1A']
        for i,key in enumerate(keys):
            start=len(requests);scene(page,http,key)
            panel=page.locator('.density-options');assert not panel.evaluate('(x)=>x.open')
            assert panel.locator('img').count()==0
            new_requests=requests[start:];assert not any('/media/density_' in u for u in new_requests),(key,'density fetched before opening')
            # Scientific qualification propagation is checked independently of density visibility.
            if key.startswith('7COY_') and key.endswith(('_A1A','_special_pair')):
                assert 'Local-density qualification:' in page.locator('#view-notes').inner_text()
            if key.startswith(('9S6P_','9SK3_')) and key.endswith(('_P_A','_special_pair')):
                assert 'Site-water qualification:' in page.locator('#view-notes').inner_text()
            if key.startswith('5OY0_prot3_') and key.endswith(('_P_A','_special_pair')):
                assert 'Axial-geometry qualification:' in page.locator('#view-notes').inner_text()
            values=page.locator('#ctable tr[data-i] td.num').all_text_contents()
            expected=page.evaluate("key=>window.PSI_VIEWS[key].contacts.map(c=>c.d.toFixed(2)).sort()",key)
            assert sorted(values)==expected,(key,values,expected)
            assert page.locator('[data-l="residueLabels"]').get_attribute('aria-pressed')=='true'
            assert page.locator('[data-l="distanceLabels"]').get_attribute('aria-pressed')=='true'
            assert page.locator('[data-s="common"]').get_attribute('aria-pressed')=='true'
            assert page.locator('[data-m="off"]').get_attribute('aria-pressed')=='true'
            label_count=page.evaluate("window.__psiText.filter(t=>t.connected).length")
            assert label_count>0,(key,'no canvas text')
            if key[:4] in additions and not a.smoke:shot(page,key,canvas=True)
            page.locator('.density-options summary').click();images_ready(page)
            item=density['scenes'][key];assert panel.locator('img').count()==len(item['sections'])
            if item['status']=='unavailable':assert 'No released experimental data' in panel.inner_text()
            for im in item['sections']:assert panel.locator('img[src="'+im['src']+'"]').count()==1
            panel.locator('[data-density="meshes"]').click();images_ready(page);assert panel.locator('img').count()==len(item['meshes'])
            for im in item['meshes']:assert panel.locator('img[src="'+im['src']+'"]').count()==1
            if item['status']=='unavailable':assert 'No released experimental data' in panel.inner_text()
            panel.locator('[data-density="sections"]').click();images_ready(page)
            page.locator('.density-options summary').click();assert not panel.evaluate('(x)=>x.open')
            result['scenes'].append(dict(scene=key,table_rows=len(values),original_label_toggles=True,common_scale=True,closed_lazy_default=True,sections=len(item['sections']),meshes=len(item['meshes']),status=item['status']))
            if (i+1)%20==0:print(json.dumps(dict(scene_checks=i+1)),flush=True);save()
        # Exercise original scene controls through actual browser events.
        scene(page,http,'9LUT_prot1_special_pair')
        for attr,value in [('data-m','spin'),('data-m','rock'),('data-m','off'),('data-s','whole'),('data-s','common')]:
            control=page.locator(f'[{attr}="{value}"]');control.click();assert control.get_attribute('aria-pressed')=='true'
        for label in ['residueLabels','distanceLabels']:
            button=page.locator(f'[data-l="{label}"]');button.click();assert button.get_attribute('aria-pressed')=='false';button.click();assert button.get_attribute('aria-pressed')=='true'
        cv=page.locator('#stage canvas');before=cv.screenshot();box=cv.bounding_box();page.mouse.move(box['x']+box['width']*.4,box['y']+box['height']*.5);page.mouse.down();page.mouse.move(box['x']+box['width']*.6,box['y']+box['height']*.55,steps=8);page.mouse.up();assert cv.screenshot()!=before
        cv.focus();page.keyboard.press('ArrowLeft');page.keyboard.press('+');page.keyboard.press('r');page.locator('#reset').click()
        first=page.locator('#ctable tr[data-i]').first;idx=first.get_attribute('data-i');first.click();assert not page.locator(f'#ctable tr[data-for="{idx}"]').evaluate('(x)=>x.hidden');first.click()
        legend=page.locator('#legend button').first;legend.click();assert legend.get_attribute('aria-pressed')=='false';legend.click();assert legend.get_attribute('aria-pressed')=='true'
        page.locator('#fs').click();assert page.evaluate('!!document.fullscreenElement');page.locator('#fs').click();assert not page.evaluate('!!document.fullscreenElement')
        page.locator('#stage canvas').focus();page.keyboard.press(']');page.wait_for_function("location.hash.includes('8WEY_prot1_special_pair')");page.go_back();page.wait_for_function("location.hash.includes('9LUT_prot1_special_pair')")
        result['interactions'].append(dict(status='PASS',checks=['Spin/Rock/Hold','Common/whole scale','Residue/distance labels','Drag rotation','Keyboard rotation/zoom/reset','Row detail','Class toggle','Fullscreen enter/exit','Next protomer key','Back history']))
        # Quantitative comparisons, sorting, missing reasons, matrix downloads.
        for part in atlas['parts']:
            page.goto(http+'#/compare/'+part['route']);page.wait_for_selector('#matrix tbody tr')
            assert page.locator('#matrix tbody tr').count()==40
            texts=page.locator('#matrix td.v a').all_text_contents();want=page.evaluate("part=>window.PSI_ATLAS.compare[part].flatMap(row=>row.cells.filter(c=>c.d!=null).map(c=>c.d.toFixed(2)))",part['key'])
            assert sorted(t.rstrip('†') for t in texts)==sorted(want)
            assert page.locator('#matrix td.na').evaluate_all('(xs)=>xs.every(x=>x.title.length>0)')
            assert 'eight additions' in page.locator('#app').inner_text() and 'not biological replicates' in page.locator('#app').inner_text()
            page.locator('.colsort').first.click();assert page.locator('th.sorted').count()==1;page.locator('#sort-reset').click();assert page.locator('th.sorted').count()==0
            result['comparisons'].append(dict(part=part['key'],rows=40,numeric_cells=len(texts),missing_reason_tooltips=True,sort_reset=True))
        info,_=download(page,'a[download][href="downloads/compare_matrix.csv"]','http_matrix',R/'downloads/compare_matrix.csv');result['downloads'].append(info)
        # Responsive/light/dark layouts: original molecular labels preserved.
        routes=['#/','#/view/9LUT_prot1_special_pair','#/view/9KZ9_prot1_P_A','#/view/7DKZ_prot1_A1A','#/view/9HYU_prot1_A1B','#/compare/pa-network','#/methods']
        for width,height in [(1440,1100),(768,1024),(390,844)]:
            page.set_viewport_size({'width':width,'height':height})
            for theme in ['light','dark']:
                page.evaluate("theme=>{document.documentElement.dataset.theme=theme;localStorage.setItem('psi-theme',theme)}",theme)
                for route in routes:
                    page.goto(http+route)
                    if '/view/' in route:scene(page,http,route.split('/view/')[1])
                    elif route=='#/':page.wait_for_selector('#hero-host canvas')
                    elif '/compare/' in route:page.wait_for_selector('#matrix tbody tr')
                    else:page.wait_for_selector('h1')
                    metrics=page.evaluate("""() => ({width:innerWidth,scrollWidth:document.documentElement.scrollWidth,theme:document.documentElement.dataset.theme,background:getComputedStyle(document.body).backgroundColor})""")
                    if metrics['scrollWidth']>width+1:result['issues'].append(dict(kind='page_overflow',route=route,viewport=width,theme=theme,metrics=metrics))
                    tag=route.replace('#/','').replace('/','_') or 'home';shot(page,f'{tag}_{width}_{theme}')
                    result['layouts'].append(dict(route=route,**metrics))
                    if route=='#/view/9KZ9_prot1_P_A':
                        assert '3.05697' in page.locator('#view-notes').inner_text()
                if width==390:
                    scene(page,http,'9AU4_prot3_P_A');page.locator('.density-options summary').click();images_ready(page);page.locator('[data-density="meshes"]').click();images_ready(page);shot(page,f'9AU4_p3_density_phone_{theme}')
        page.set_viewport_size({'width':1440,'height':1100});page.evaluate("document.documentElement.dataset.theme='light'")
        # Site-specific notice relevance and collapsed evidence are part of this release review.
        for pdb,count,word in [('7DKZ',2,'Alaska'),('9UH3',0,'α-DDM'),('9HYU',0,'combined'),('9LUT',0,'Tak-1')]:
            page.goto(http+'#/structure/'+pdb);page.wait_for_selector('.entry-head')
            assert page.locator('#app p.note').count()==count,(pdb,'unexpected default warnings')
            details=page.locator('.review-provenance');assert not details.evaluate('(x)=>x.open')
            details.locator('summary').click();assert word in details.inner_text()
            shot(page,pdb+'_notice_structure_reviewed')
        scene(page,http,'7DKZ_prot1_A1B');assert page.locator('#view-notes > p.note').count()==1
        text=page.locator('#view-notes > p.note').inner_text();assert 'bent' in text and 'working on interpretations' in text
        assert not page.locator('.review-provenance').evaluate('(x)=>x.open');shot(page,'7DKZ_A1B_curator_note')
        scene(page,http,'7DKZ_prot1_P_A');assert page.locator('#view-notes > p.note').count()==1
        assert 'A923' in page.locator('#view-notes > p.note').inner_text()
        # User theme toggle persists through actual reload.
        page.locator('#theme').click();selected=page.evaluate('document.documentElement.dataset.theme');page.reload();assert page.evaluate('document.documentElement.dataset.theme')==selected
        page.locator('#theme').click()
        # Actual exports and downloads for all four environment types in HTTP and file delivery modes.
        export_keys=['9LUT_prot1_special_pair','9KZ9_prot1_P_A','7DKZ_prot1_A1A','9HYU_prot1_A1B']
        for mode,base in [('http',http),('file',file)]:
            export_page=page if mode=='http' else capture_context(browser,'file')[0]
            export_page.set_viewport_size({'width':1440,'height':1100})
            for key in export_keys:
                scene(export_page,base,key);export_page.evaluate('window.__psiText=[]')
                info,dest=download(export_page,'#png',mode+'_'+key)
                with Image.open(dest) as im:assert im.format=='PNG' and im.width==2560;info.update(format='PNG',dimensions=list(im.size))
                captions=export_page.evaluate('window.__psiText.filter(x=>x.caption&&!x.connected)');assert captions
                info['caption_draws']=captions
                for c in captions:
                    if c['x']+c['width']>c['canvasW']:result['issues'].append(dict(kind='export_caption_clipped',mode=mode,scene=key,format='PNG',caption=c))
                result['exports'].append(info)
                export_page.locator('#gifbtn').click();assert export_page.locator('[data-gt="10"]').get_attribute('aria-pressed')=='true'
                export_page.locator('[data-gt="6"]').click()
                info,dest=download(export_page,'#gif-go',mode+'_'+key)
                with Image.open(dest) as im:
                    assert im.format=='GIF' and im.width==480 and im.n_frames==75
                    durations=[];digests=set()
                    for n in range(im.n_frames):im.seek(n);durations.append(im.info.get('duration'));digests.add(hashlib.sha256(im.convert('RGB').tobytes()).hexdigest())
                    assert set(durations)=={80} and len(digests)>60
                    info.update(format='GIF',dimensions=list(im.size),frames=im.n_frames,frame_duration_ms=80,unique_frames=len(digests),total_duration_ms=sum(durations),loop=im.info.get('loop'))
                assert export_page.locator('#gif-status').inner_text().startswith('Saved ')
                result['exports'].append(info)
                export_page.locator('summary').filter(has_text='Downloads & archive').click()
                for kind in ['contacts','cif','pymol']:
                    rel=export_page.evaluate('([key,kind])=>window.PSI_VIEWS[key].downloads[kind]',[key,kind]);assert key in rel
                    info,_=download(export_page,f'a[download][href="{rel}"]',mode+'_'+key+'_'+kind,R/rel);result['downloads'].append(info)
            # At phone width, export text must remain within the image, too.
            export_page.set_viewport_size({'width':390,'height':844});scene(export_page,base,'9LUT_prot1_special_pair');export_page.evaluate('window.__psiText=[]')
            info,dest=download(export_page,'#png',mode+'_phone_9LUT')
            with Image.open(dest) as im:info.update(format='PNG',dimensions=list(im.size))
            captions=export_page.evaluate('window.__psiText.filter(x=>x.caption&&!x.connected)');info['caption_draws']=captions
            for c in captions:
                if c['x']+c['width']>c['canvasW']:result['issues'].append(dict(kind='export_caption_clipped',mode=mode,scene='9LUT_prot1_special_pair',viewport=390,format='PNG',caption=c))
            result['exports'].append(info)
        result['status']='PASS' if not result['issues'] and not result['errors'] and not result['request_failures'] else 'ISSUES_FOUND'
        result['scope_limits']='Real headless Windows desktop browsers at emulated viewport widths; not a physical mobile, Safari, Firefox or accessibility audit. Browser rendering checks do not establish scientific model quality.'
        save();print(json.dumps({k:(len(v) if isinstance(v,list) else v) for k,v in result.items() if k not in ['executable','isolation','scope_limits']}),flush=True)
        for context in page_contexts:context.close()
        browser.close()
except BaseException:
    result['status']='HARNESS_OR_APPLICATION_FAILURE';result['exception']=traceback.format_exc();save();print(result['exception'],flush=True);raise
finally:server.shutdown();server.server_close()
