'use strict';
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict'),path=require('node:path');
const root=process.argv[2],out=process.argv[3];
class Node {
 constructor(){this.handlers={};this.attrs={};this.children=[];this.open=false;this._html='';}
 addEventListener(n,f){(this.handlers[n]??=[]).push(f);} removeEventListener(n,f){this.handlers[n]=(this.handlers[n]||[]).filter(x=>x!==f);}
 fire(n){for(const f of this.handlers[n]||[])f({target:this});} setAttribute(k,v){this.attrs[k]=v;} getAttribute(k){return this.attrs[k];} appendChild(n){this.children.push(n);}
 set innerHTML(v){this._html=v;if(v.includes('density-content')){this.content=new Node();this.buttons=['sections','meshes'].map(mode=>{const b=new Node();b.dataset={density:mode};return b;});}}
 get innerHTML(){return this._html;} querySelector(s){assert.equal(s,'.density-content');return this.content;} querySelectorAll(s){assert.equal(s,'[data-density]');return this.buttons;}
}
const ctx={document:{createElement(){return new Node();}}};ctx.window=ctx;vm.createContext(ctx);
for(const f of ['data/atlas.js','data/density_review.js','data/release_notices.js','js/density_review.js'])vm.runInContext(fs.readFileSync(path.join(root,f),'utf8'),ctx,{filename:f,timeout:1000});
let total=0,unavailable=0,images=0;const protomers=new Set();
for(const structure of ctx.window.PSI_ATLAS.structures)for(const prot of structure.protomers)for(const view of prot.views){
 vm.runInContext(fs.readFileSync(path.join(root,'data/views',view.key+'.js'),'utf8'),ctx,{timeout:1000});
 const sc=ctx.window.PSI_VIEWS[view.key],item=ctx.window.PSI_DENSITY.scenes[view.key],host=new Node(),api=ctx.window.PSIDensity.mount(host,sc),panel=host.children[0];
 assert(api,view.key+' missing optional panel');assert.equal(panel.open,false);assert.equal(panel.content.innerHTML,'');
 panel.open=true;panel.fire('toggle');assert.equal((panel.content.innerHTML.match(/<img /g)||[]).length,item.sections.length);
 if(item.status==='unavailable'){assert(panel.content.innerHTML.includes('role="status"'));assert(panel.content.innerHTML.includes('No released experimental data'));unavailable++;}
 for(const im of item.sections){assert(panel.content.innerHTML.includes(im.src));assert(im.src.includes(view.key));}
 panel.buttons[1].fire('click');assert.equal(panel.buttons[1].getAttribute('aria-pressed'),'true');assert.equal(panel.buttons[0].getAttribute('aria-pressed'),'false');assert.equal((panel.content.innerHTML.match(/<img /g)||[]).length,item.meshes.length);
 if(item.status==='unavailable')assert(panel.content.innerHTML.includes('role="status"'));
 for(const [i,im] of item.meshes.entries()){assert(panel.content.innerHTML.includes(im.src));assert(im.src.includes(view.key));assert(panel.content.innerHTML.includes('density.html?scene='+view.key+'&preset='+i));assert(panel.content.innerHTML.includes('Static PNG'));}
 panel.buttons[0].fire('click');assert.equal((panel.content.innerHTML.match(/<img /g)||[]).length,item.sections.length);
 api.destroy();assert.equal(panel.handlers.toggle.length,0);assert(panel.buttons.every(b=>b.handlers.click.length===0));
 protomers.add(structure.pdb+':'+prot.number);total++;images+=item.sections.length+item.meshes.length;
}
assert.equal(total,160);assert.equal(protomers.size,40);assert.equal(unavailable,4);
assert.equal(Object.values(ctx.window.PSI_DENSITY.entries).filter(e=>e.reviewed).length,21);
const original=['Local density has not been visually reviewed; no hydrogen-bond assignment.'];
const q=ctx.window.PSIDensity.reviewNotes('7DKZ',original,{part:'A1B',protomer:1});
assert.equal(q.length,1);assert(q[0].includes('bent'));assert(q[0].includes('working on interpretations'));
assert(!q.join(' ').includes('not individually reviewed'));assert(!q.join(' ').includes('A923'));
const water=ctx.window.PSIDensity.reviewNotes('7DKZ',original,{part:'P_A',protomer:1});assert.equal(water.length,1);assert(water[0].includes('A923'));
assert.equal(ctx.window.PSIDensity.reviewNotes('9UH3',original).length,0);
assert(ctx.window.PSIDensity.reviewNotes('9KZ9',original,{part:'P_A'}).join(' ').includes('3.05697'));
assert.equal(ctx.window.PSIDensity.reviewNotes('5OY0',original,{part:'P_A',protomer:1}).length,0);
assert(ctx.window.PSIDensity.reviewNotes('5OY0',original,{part:'P_A',protomer:3}).join(' ').includes('3.92402'));
assert(ctx.window.PSIDensity.reviewNotes('1JB0',original).join(' ').includes('No released experimental'));
assert(original[0].includes('has not been visually reviewed'));
const missing=new Node();assert.equal(ctx.window.PSIDensity.mount(missing,{key:'NOT_AN_ATLAS_SCENE',pdb:'1JB0',protomer:1}),null);assert.equal(missing.children.length,0);
const result={status:'PASS',scene_panels:total,protomers:protomers.size,unavailable_panels:unavailable,image_references:images,checks:['Closed default and lazy image creation for every scene','Section/mesh switching','Native scene/protomer asset identity','Explicit unavailable-data messages in both modes','No automatic promotion of unreviewed maps','Prior scientific flags retained','No mutation of source notes','Event cleanup','Unknown-scene fallback'],limitation:'DOM contract harness; no browser control, screenshot or browser interaction test.'};
fs.writeFileSync(out,JSON.stringify(result,null,2));console.log(JSON.stringify(result));
