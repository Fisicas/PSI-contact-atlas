from pathlib import Path
import argparse,sys,json,http.server,threading,functools,time,hashlib
arg=argparse.ArgumentParser();arg.add_argument('--all',action='store_true');arg.add_argument('--repo',type=Path,default=Path(__file__).resolve().parents[2]);arg.add_argument('--output',type=Path,required=True);arg.add_argument('--runtime-dir',type=Path,help='Existing Playwright Python package directory, if outside the selected environment');args=arg.parse_args();R=args.repo.resolve();W=args.output.resolve();(W/'reports').mkdir(parents=True,exist_ok=True);(W/'browser_review').mkdir(exist_ok=True)
if args.runtime_dir:sys.path.insert(0,str(args.runtime_dir))
from playwright.sync_api import sync_playwright
tag='all' if args.all else 'smoke'
index=json.loads((R/'data/density_interactive_index.js').read_text(encoding='utf-8').split('=',1)[1].strip().rstrip(';'));available=[k for k,v in index['scenes'].items() if v['status']=='available'];representatives=['9YL7_prot1_A1A','5OY0_prot3_P_A','7DKZ_prot1_A1B','9AU4_prot1_A1A','9HYU_prot1_special_pair','9EYS_prot3_P_A','9OZ3_prot3_A1B'];keys=available if args.all else representatives
class Handler(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*x):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(R)));threading.Thread(target=server.serve_forever,daemon=True).start();errors=[];rows=[];interactions=[];thumbs=[]
def ready(page):
 page.wait_for_function("window.DENSITY_APP?.ready || !document.getElementById('error').hidden",timeout=30000)
 assert page.evaluate('!!window.DENSITY_APP?.ready'),page.locator('#error').inner_text()
frame_script='''async()=>{const A=DENSITY_APP,D=A.payload;let maps=[];for(const [kind,v]of Object.entries(A.volumes)){const g=D.maps[kind].grid;const data=new Uint8Array(v.data.buffer,v.data.byteOffset,v.data.byteLength);const hash=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',data))).map(x=>x.toString(16).padStart(2,'0')).join('');let maxPosition=0,maxValue=0;for(const s of g.sample_checks){let p=new $3Dmol.Vector3(...s.ijk);if(v.matrix)p.applyMatrix4(v.matrix);else{p.x=v.origin.x+s.ijk[0]*v.unit.x;p.y=v.origin.y+s.ijk[1]*v.unit.y;p.z=v.origin.z+s.ijk[2]*v.unit.z;}maxPosition=Math.max(maxPosition,...[p.x,p.y,p.z].map((x,i)=>Math.abs(x-s.xyz_A[i])));let value=v.getVal(...s.xyz_A);if(s.value!==null)maxValue=Math.max(maxValue,Math.abs(value-s.value));else if(!Number.isNaN(value))throw Error('NaN map value changed');}maps.push({kind,hash,expected:g.data_sha256,voxels:v.data.length,max_position_error_A:maxPosition,max_value_error:maxValue});}const atoms=A.model.selectedAtoms({});let atomError=Math.max(...atoms.map((a,i)=>Math.max(Math.abs(a.x-D.scene.atoms[i][3]),Math.abs(a.y-D.scene.atoms[i][4]),Math.abs(a.z-D.scene.atoms[i][5]))));let eligible=new Set(),polar=new Set();for(const c of D.scene.contacts){if((c.cls==='polar'&&c.basis==='donor–acceptor compatible')||c.cls==='water'){eligible.add(c.i);eligible.add(c.j);}if(c.cls==='polar'&&c.basis==='donor–acceptor compatible'){polar.add(c.i);polar.add(c.j);}}let options=[...document.querySelectorAll('#atoms option')].map(x=>+x.value);let first=options.slice(0,eligible.size);const priority=eligible.size===first.length&&first.every(x=>eligible.has(x))&&(!polar.size||polar.has(options[0]));return {maps,atoms:atoms.length,expected_atoms:D.scene.atoms.length,atom_error_A:atomError,candidate_priority:priority,candidate_atoms:eligible.size,option_count:options.length,unique_options:new Set(options).size,first_group:document.querySelector('#atoms optgroup')?.label,level:+document.getElementById('level').value,presets:DENSITY_APP.item.presets.length,units:D.units};}'''
try:
 with sync_playwright() as pw:
  browser=pw.chromium.launch(executable_path=str(Path(__import__('os').environ.get('PROGRAMFILES',r'C:\Program Files'))/'Google/Chrome/Application/chrome.exe'),headless=True,args=['--disable-background-networking','--no-first-run','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
  context=browser.new_context(viewport={'width':1440,'height':1100},accept_downloads=True);context.route('**/*',lambda rt:rt.continue_() if rt.request.url.startswith(('http://127.0.0.1:','file:','data:','blob:')) else rt.abort());page=context.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
  for scheme,base in [('HTTP',f'http://127.0.0.1:{server.server_port}/density.html'),('file',(R/'density.html').as_uri())]:
   for n,key in enumerate(keys,1):
    if page.evaluate('!!window.DENSITY_APP?.destroy'):page.evaluate('DENSITY_APP.destroy()')
    start=time.monotonic();page.goto(base+'?scene='+key+'&preset=0');ready(page);result=page.evaluate(frame_script)
    assert all(x['hash']==x['expected'] and x['max_position_error_A']<2e-4 and x['max_value_error']<1e-7 for x in result['maps']),(key,result)
    assert result['atoms']==result['expected_atoms']==result['option_count']==result['unique_options'] and result['atom_error_A']==0 and result['candidate_priority'],(key,result)
    preset_count=0
    for i,preset in enumerate(index['scenes'][key]['presets']):
     page.locator('#preset').select_option(str(i));assert abs(float(page.locator('#level').input_value())-preset['level'])<1e-9,(key,i);assert page.locator(f'#fallback a[href="{preset["image"]}"]').count()==1;preset_count+=1
    rows.append(dict(scheme=scheme,scene=key,status='PASS',seconds=round(time.monotonic()-start,3),presets_checked=preset_count,**result))
    if key in representatives:
     box=page.locator('#viewer').bounding_box();x=box['x']+box['width']/2;y=box['y']+box['height']/2;initial=page.evaluate('DENSITY_APP.viewer.getView()')
     page.mouse.move(x,y);page.mouse.down();page.mouse.move(x+80,y+30,steps=6);page.mouse.up();assert page.evaluate('DENSITY_APP.viewer.getView()')!=initial
     page.locator('#pan').click();before=page.evaluate('DENSITY_APP.viewer.getView()');page.mouse.move(x,y);page.mouse.down();page.mouse.move(x+45,y+20,steps=6);page.mouse.up();after=page.evaluate('DENSITY_APP.viewer.getView()');assert before!=after and before[4:]==after[4:]
     page.mouse.wheel(0,-130);page.wait_for_timeout(80);assert page.evaluate('DENSITY_APP.viewer.getView()')!=after;page.locator('#reset').click();assert page.evaluate('DENSITY_APP.viewer.getView()')==initial;page.locator('#rotate').click()
     page.locator('#source-level').click();page.locator('#level').focus();page.locator('#level').press('ArrowRight');page.wait_for_timeout(60);page.locator('#source-level').click();assert abs(float(page.locator('#level').input_value())-page.evaluate('DENSITY_APP.payload.source_level'))<1e-9
     page.locator('#opacity').press('ArrowLeft');page.locator('#carve').uncheck();page.locator('#carve').check();page.locator('#wire').uncheck();page.locator('#wire').check();page.locator('#density').uncheck();page.locator('#density').check();
     if 'difference' in page.evaluate('Object.keys(DENSITY_APP.volumes)'):page.locator('#difference').uncheck();page.locator('#difference').check();assert page.evaluate('DENSITY_APP.active_shapes.length')==3
     # Candidate atom and partner choices, plus actual WebGL mouse picking.
     first=page.locator('#atoms option').first.get_attribute('value');page.select_option('#atoms',first);assert 'Native XYZ' in page.locator('#atom-info').inner_text();assert page.locator('#atom-info [data-partner]').count()>0;page.locator('#atom-info [data-partner]').first.click()
     picked=False;page.locator('#reset').click()
     for j in range(6):
      point=page.evaluate('(i)=>DENSITY_APP.viewer.modelToScreen([DENSITY_APP.model.selectedAtoms({})[i]])[0]',j);old=page.locator('#atoms').input_value();page.mouse.click(point['x'],point['y'])
      if page.locator('#atoms').input_value()!=old:picked=True;break
     assert picked,(key,'atom picking')
     page.locator('#contacts button').first.click();assert 'computational precision' in page.locator('#atom-info').inner_text();page.locator('#guides').check();page.locator('#guides').uncheck();page.locator('#reset').click()
     if scheme=='HTTP':
      for button,filename in [('png',key+'_export.png'),('map-download',key+'_primary.ccp4'),('cif-download',key+'.cif')]:
       page.locator('details').evaluate('(e)=>e.open=true')
       with page.expect_download() as dl:page.locator('#'+button).click()
       target=W/'browser_review'/filename;dl.value.save_as(target)
       if button=='map-download':assert hashlib.sha256(target.read_bytes()).hexdigest()==page.evaluate('DENSITY_APP.payload.maps.primary.sha256')
      page.locator('details').evaluate('(e)=>e.open=false');page.locator('#theme').click();page.screenshot(path=str(W/'browser_review'/(key+'_desktop.png')),full_page=True);page.set_viewport_size({'width':390,'height':844});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1');page.screenshot(path=str(W/'browser_review'/(key+'_phone.png')),full_page=True);page.set_viewport_size({'width':1440,'height':1100})
     interactions.append(dict(scheme=scheme,scene=key,mouse_rotation=True,hand_pan=True,wheel_zoom=True,reset_exact=True,contour_reset=True,opacity_carve_surface_density=True,candidate_partners=True,atom_mouse_pick=True,contact_rows=True))
    if n%12==0 or n==len(keys):print(scheme,n,'/',len(keys),'scenes pass',flush=True)
   for key,item in index['scenes'].items():
    if item['status']!='unavailable':continue
    page.goto(base+'?scene='+key);ready(page);assert page.evaluate('DENSITY_APP.unavailable') and not page.locator('#viewer').is_visible() and page.locator('canvas').count()==0
  # Click real mesh thumbnails from representative atlas pages and confirm destination/preset.
  for key in representatives:
   page.goto(f'http://127.0.0.1:{server.server_port}/index.html?still=1#/view/'+key);page.wait_for_selector('#stage canvas');details=page.locator('.density-options');details.evaluate('(e)=>e.open=true');page.locator('[data-density="meshes"]').click();count=len(index['scenes'][key]['presets'])
   for i in range(count):
    link=page.locator('.density-figures figure').nth(i).locator('a:has(img)');assert f'scene={key}&preset={i}' in link.get_attribute('href')
    with page.expect_popup() as popup:link.click()
    p=popup.value;ready(p);assert abs(float(p.locator('#level').input_value())-index['scenes'][key]['presets'][i]['level'])<1e-9;p.close();thumbs.append(dict(scene=key,preset=i))
   assert page.locator('.density-figures a:text-is("Static PNG")').count()==count
  assert not errors,errors
  report=dict(status='PASS',mode=tag,browser=browser.version,WebGL='Isolated Chrome with SwiftShader software WebGL',scene_loads=len(rows),unique_scenes=len(keys),map_parser_checks=sum(len(x['maps']) for x in rows),checked_voxels=sum(v['voxels'] for x in rows for v in x['maps']),candidate_priority_all=True,rows=rows,interaction_checks=interactions,actual_mesh_thumbnail_clicks=thumbs,unavailable_scenes=4,JS_errors=errors,input_bindings_sha256={rel:hashlib.sha256((R/rel).read_bytes()).hexdigest() for rel in ['density.html','js/density_viewer.js','css/density_viewer.css','js/density_review.js','data/density_interactive_index.js']},scope='Exact voxel-byte hashes plus physical affine/sample-value checks, source coordinates and candidate ordering for every requested scene over local HTTP and file protocols. Representative full interactions, downloads and mobile/dark layouts; hardware GPU and independent scientific interpretation are not established.')
  (W/'reports'/f'interactive_browser_{tag}_v06.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('BROWSER',tag,'PASS',len(rows),'scene loads',flush=True);context.close();browser.close()
finally:server.shutdown();server.server_close()
