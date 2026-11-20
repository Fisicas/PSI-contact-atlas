"""Native-resolution local-density figures for every deposited atlas protomer.

No coordinate refinement, smoothing, map sharpening or EM normalization.
"""
import argparse,copy,csv,gc,hashlib,json,math,re,sys,time
from pathlib import Path
import gemmi
import numpy as np
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
from common import config,source as load_source,frame as bind_frame
ARGS=config();R=ARGS.repo;N=ARGS.work_dir

sys.dont_write_bytecode=True;sys.path.insert(0,str(R/'tools'));import build_atlas as BA

def js(path,prefix='PSI_ATLAS'):
    t=path.read_text(encoding='utf-8');return json.loads(t[t.index('=',t.index(prefix))+1:].strip().rstrip(';'))
def write(p,obj):p.write_text(json.dumps(obj,indent=2),encoding='utf-8')
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
    return h.hexdigest()
def native_id(sc,i):
    a=sc['atoms'][i];r=sc['residues'][a[2]];return f"{r['comp']}:{r['chain']}:{r['num']}:{a[0]}"
def frac_box(cell,xyz,pad=5.):
    lo=xyz.min(axis=0)-pad;hi=xyz.max(axis=0)+pad;corners=np.array([[x,y,z] for x in [lo[0],hi[0]] for y in [lo[1],hi[1]] for z in [lo[2],hi[2]]]);f=np.array([list(cell.fractionalize(gemmi.Position(*p))) for p in corners]);b=gemmi.FractionalBox();b.minimum=gemmi.Fractional(*f.min(axis=0));b.maximum=gemmi.Fractional(*f.max(axis=0));return b
def save_crop(grid,path,xyz,tolerance):
    cc=gemmi.Ccp4Map();cc.grid=grid.clone();cc.update_ccp4_header(2,True);cc.set_extent(frac_box(grid.unit_cell,xyz));cc.write_ccp4_map(str(path));del cc
    check=gemmi.read_ccp4_map(str(path),setup=True);a=grid.interpolate_position_array(xyz,order=1);b=check.grid.interpolate_position_array(xyz,order=1);error=float(np.max(abs(a-b)));assert error<tolerance,(path,error);del check
    return dict(file=str(path.relative_to(N)),margin_A=5.,max_sampling_roundtrip_error=error,allowed_roundtrip_error=tolerance,serialization_note='CCP4 stores unit-cell parameters as float32; source SF cell precision can cause small interpolation differences even when voxel values are retained.')
def valid_positions(grid,xyz,extent):
    if extent is None:return np.ones(len(xyz),dtype=bool)
    # Orthogonal EM source grids; check their actual physical extent before sampling.
    matrix=np.array(grid.unit_cell.frac.mat);offset=np.array(list(grid.unit_cell.frac.vec));frac=xyz@matrix.T+offset
    return np.all((frac>=np.array(extent[0])-1e-7)&(frac<=np.array(extent[1])+1e-7),axis=1)
def sample(grid,xyz,extent):
    good=valid_positions(grid,xyz,extent);values=grid.interpolate_position_array(np.ascontiguousarray(xyz,dtype=np.float64),order=1);values[~good]=np.nan;return values,good
def plot(sc,grid,diff,level,extent,folder,name,points,targets,level_basis):
    pts=np.array(points);center=pts.mean(axis=0);u=pts[1]-pts[0];u/=np.linalg.norm(u);normal=np.cross(u,pts[2]-pts[0]);assert np.linalg.norm(normal)>1e-6;normal/=np.linalg.norm(normal);v=np.cross(normal,u)
    axis=np.linspace(-7,7,101);xx,yy=np.meshgrid(axis,axis,indexing='xy');xyz=np.ascontiguousarray(center+xx[...,None]*u+yy[...,None]*v,dtype=np.float64);values,good=sample(grid,xyz.reshape(-1,3),extent);values=values.reshape(xx.shape)
    fig,ax=plt.subplots(figsize=(7.4,7.4));fig.subplots_adjust(left=.11,right=.98,bottom=.17,top=.84)
    ax.imshow(values,origin='lower',extent=[-7,7,-7,7],cmap='Greys',vmin=0,vmax=3*level if diff is None else 3.,alpha=.8,interpolation='nearest')
    levels=[.8*level,level,1.2*level] if diff is None else [1.,1.5];colors=['#8bc8e8','#1565a8','#07366a'] if diff is None else ['#72b2df','#124f9b']
    for lev,color in zip(levels,colors):
        if np.nanmin(values)<lev<np.nanmax(values):ax.contour(xx,yy,values,levels=[lev],colors=[color],linewidths=.8)
    if diff is not None:
        dv=diff.interpolate_position_array(xyz.reshape(-1,3),order=1).reshape(xx.shape)
        for lev,color in [(-3.,'#ca2334'),(3.,'#008b45')]:
            if dv.min()<lev<dv.max():ax.contour(xx,yy,dv,levels=[lev],colors=[color],linewidths=1.15)
    delta=np.array([a[3:6] for a in sc['atoms']])-center;px=delta@u;py=delta@v;pz=delta@normal
    for i,j,_ in sc['bonds']:
        if abs(pz[i])<=1 and abs(pz[j])<=1:ax.plot([px[i],px[j]],[py[i],py[j]],color='#333333',lw=1.5,zorder=4)
    labelled=[]
    for i,a in enumerate(sc['atoms']):
        if abs(pz[i])>1:continue
        color={'O':'#de2727','N':'#204dc4','Mg':'#188943','S':'#b28d00'}.get(a[1],'#555555');ax.scatter(px[i],py[i],s=20 if a[1]!='Mg' else 38,c=color,edgecolors='white',linewidths=.3,zorder=5)
        if native_id(sc,i) in targets:labelled.append((native_id(sc,i),px[i],py[i]))
    labelled.sort(key=lambda q:(-q[2],q[1]));slots=[(.56,.89),(.06,.15),(.56,.08)] if len(labelled)>=3 else [(.56,.89),(.06,.12)]
    for (ident,x,y),slot in zip(labelled,slots):ax.annotate(ident,(x,y),xytext=slot,textcoords='axes fraction',ha='left',fontsize=8,bbox=dict(fc='white',ec='#ccc',alpha=.95,pad=2),arrowprops=dict(arrowstyle='-',color='#666',lw=.65),zorder=6)
    units=f'EM {level:g} raw units; 0.8/1.0/1.2 × {level_basis}' if diff is None else 'Weighted main 1.0/1.5 full-cell σ; difference ±3 full-cell σ'
    ax.set(title=f"{sc['pdb']} · protomer {sc['protomer']} · {sc['part']}\n{name.replace('_',' ')}\n{units}",xlabel='Local plane coordinate (Å)',ylabel='Local plane coordinate (Å)',xlim=(-7,7),ylim=(-7,7),aspect='equal');ax.title.set_fontsize(10);ax.xaxis.label.set_fontsize(9);ax.yaxis.label.set_fontsize(9);ax.tick_params(labelsize=8)
    fig.text(.015,.025,'Unmasked section; trilinear sampling (0.14 Å). Native model atoms within ±1 Å of plane shown.\nNo smoothing or refinement; oversampling adds no experimental resolution.\nPixels outside the deposited map extent are blank; crystallographic maps are periodic.',fontsize=7)
    out=folder/(sc['key']+'_'+name+'.png');fig.savefig(out,dpi=150);plt.close(fig)
    return dict(file=str(out.relative_to(N)),label=name.replace('_',' '),plane_center_A=center.tolist(),plane_u=u.tolist(),plane_v=v.tolist(),plane_normal=normal.tolist(),sample_spacing_A=.14,model_slab_half_thickness_A=1.,source_coverage_fraction=float(np.mean(good)),target_atoms=sorted(targets))
def carbonyls(comp):
    b=gemmi.cif.read_file(str(R/'build/inputs/ccd'/(comp+'.cif'))).sole_block();el={gemmi.cif.as_string(x[0]):gemmi.cif.as_string(x[1]) for x in b.find('_chem_comp_atom.',['atom_id','type_symbol'])};result=[]
    for row in b.find('_chem_comp_bond.',['atom_id_1','atom_id_2','value_order']):
        a,c,order=[gemmi.cif.as_string(x) for x in row]
        if order.upper()=='DOUB' and {el[a],el[c]}=={'O','C'}:result.append((a,c) if el[a]=='O' else (c,a))
    return result
def grid_source(source):
    path=Path(source['map_file'])
    if source['method'].startswith('X-ray'):
        refl=gemmi.as_refln_blocks(gemmi.cif.read_file(str(path)))[0];labels=refl.column_labels();required=['pdbx_FWT','pdbx_PHWT','pdbx_DELFWT','pdbx_DELPHWT'];assert all(x in labels for x in required),labels
        grid=refl.transform_f_phi_to_map('pdbx_FWT','pdbx_PHWT',sample_rate=3.);diff=refl.transform_f_phi_to_map('pdbx_DELFWT','pdbx_DELPHWT',exact_size=[grid.nu,grid.nv,grid.nw]);norm={}
        for name,g in [('main',grid),('difference',diff)]:norm[name]=dict(raw_mean=float(g.array.mean(dtype=np.float64)),raw_std=float(g.array.std(dtype=np.float64)));g.normalize()
        return grid,diff,1.,None,dict(method='X-ray',normalization='Each full-cell map separately mean-subtracted and divided by its own full-cell RMS. No crop renormalization.',normalization_values=norm,coefficients=required,FFT_sample_rate=3.,contour_basis='full-cell sigma',limitation='Deposited model-phased weighted coefficients; no omit maps or re-refinement.')
    meta=json.loads(Path(source['metadata_file']).read_text(encoding='utf-8'));cc=gemmi.read_ccp4_map(str(path),setup=False);box=cc.get_extent();extent=[list(box.minimum),list(box.maximum)]
    origin=[cc.header_float(x) for x in [50,51,52]];assert max(map(abs,origin))<1e-5,('Nonzero Cartesian map origin requires explicit registration',origin)
    cc.setup(0.);grid=cc.grid
    contours=meta.get('map',{}).get('contour_list',{}).get('contour',[]);contours=contours if isinstance(contours,list) else [contours]
    selected=[c for c in contours if str(c.get('primary','')).lower()=='true']
    if not selected and len(contours)==1:selected=contours
    if selected:level=float(selected[0]['level']);basis='author contour'
    else:level=float(grid.array.mean(dtype=np.float64)+3*grid.array.std(dtype=np.float64));basis='display level (full-grid mean + 3 SD)'
    assert level>0,(source['pdb'],level)
    return grid,None,level,extent,dict(method='cryo-EM',normalization='None; native deposited voxel values retained.',contour_basis=basis,author_contours=contours,map_annotation=meta.get('map',{}).get('annotation_details'),header_origin_A=origin,original_extent_fractional=extent,limitation='Processed deposited map; no half-map cross-validation, local FSC, smoothing, sharpening or refinement.')
def prepare(s,source):
    pdb=s['pdb'];frame=bind_frame(pdb,ARGS);assert frame['status']=='PASS'
    grid,diff,level,extent,info=grid_source(source);info.update(map_file=source['map_file'],map_sha256=sha(Path(source['map_file'])),grid_size=[grid.nu,grid.nv,grid.nw],unit_cell=list(grid.unit_cell.parameters),spacegroup=grid.spacegroup.hm,primary_level=level,full_grid_mean=float(grid.array.mean(dtype=np.float64)),full_grid_std=float(grid.array.std(dtype=np.float64)))
    cfg=json.loads((R/'build/config/sources.json').read_text(encoding='utf-8'))[pdb];native=BA.Source(R/'build'/cfg['file'],cfg['sha256']);out=N/'previews_v02'/pdb;out.mkdir(exist_ok=True,parents=True);crops=N/'crops_v02'/pdb;crops.mkdir(exist_ok=True,parents=True);scenes=[];samples=[]
    for f in sorted((R/'data/views').glob(pdb+'_*.js')):
        sc=copy.deepcopy(js(f,'PSI_VIEWS['));serialized=[]
        for i,a in enumerate(sc['atoms']):
            actual=native.get(native_id(sc,i));assert actual is not None;serialized.append(float(np.linalg.norm(np.array(a[3:6])-actual['xyz'])));a[3:6]=actual['xyz'].tolist()
        xyz=np.ascontiguousarray([a[3:6] for a in sc['atoms']],dtype=np.float64);values,inside=sample(grid,xyz,extent);assert inside.all(),(sc['key'],'model atoms outside original EM source extent',xyz[~inside])
        # Ensure cropping cannot introduce periodically repeated density around EM scene atoms.
        if extent is not None:
            cropbox=frac_box(grid.unit_cell,xyz);assert np.all(np.array(list(cropbox.minimum))>=np.array(extent[0])) and np.all(np.array(list(cropbox.maximum))<=np.array(extent[1])),(sc['key'],'crop exceeds physical source extent')
        dd=diff.interpolate_position_array(xyz,order=1) if diff is not None else [None]*len(xyz)
        for i,(value,delta) in enumerate(zip(values,dd)):samples.append(dict(scene=sc['key'],atom=native_id(sc,i),x=xyz[i,0],y=xyz[i,1],z=xyz[i,2],primary_value=float(value),difference_full_cell_sigma=float(delta) if delta is not None else '',reference_level=level,unit='full-cell sigma' if diff is not None else 'raw deposited EM units'))
        tolerance=1e-4 if diff is not None else 1e-5
        record=dict(scene=sc['key'],protomer=sc['protomer'],part=sc['part'],slices=[],feature_notes=[],crops={'primary':save_crop(grid,crops/(sc['key']+'_primary.ccp4'),xyz,tolerance)},max_original_scene_rounding_A=max(serialized),coordinates='Full-precision native atoms from archived atlas source; scene serialization rounding is not propagated into these sections.')
        if diff is not None:record['crops']['difference']=save_crop(diff,crops/(sc['key']+'_difference.ccp4'),xyz,tolerance)
        lookup={native_id(sc,i):xyz[i] for i in range(len(xyz))};roles={r['role']:r for r in sc['residues'] if r.get('role')}
        def aid(role,name):r=roles[role];return f"{r['comp']}:{r['chain']}:{r['num']}:{name}"
        def add(name,ids,targets=None):
            if not all(i in lookup for i in ids):record['feature_notes'].append(name+': not drawn; required atoms are absent from the deposited scene.');return None
            result=plot(sc,grid,diff,level,extent,out,name,[lookup[i] for i in ids],set(targets or ids),info['contour_basis']);record['slices'].append(result);return result
        if sc['part'] in {'special_pair','P_A'}:
            add('P_A_ester',[aid('P_A',n) for n in ['OBD','O1D','O2D']])
            if sc['part']=='special_pair':add('P_B_ester',[aid('P_B',n) for n in ['O1A','O2A','CGA']])
            else:
                prot=next(p for p in s['protomers'] if p['number']==sc['protomer']);wid=prot.get('site_water')
                if wid and wid not in lookup and wid+':O' in lookup:wid+=':O'
                if wid and wid in lookup:add('site_water',[aid('P_A','O1D'),aid('P_A','O2D'),wid])
                else:record['feature_notes'].append('No assigned reference-site water is drawn in this scene. The P_A ester section is available; no missing water is reconstructed.')
        else:
            role='A1_A' if sc['part']=='A1A' else 'A1_B';r=roles[role];co=carbonyls(r['comp']);available=[(o,c) for o,c in co if aid(role,o) in lookup and aid(role,c) in lookup]
            missing=[o for o,c in co if aid(role,o) not in lookup]
            if missing:record['feature_notes'].append('Deposited scene lacks carbonyl atom(s): '+', '.join(missing)+'. No atoms reconstructed.')
            plane=[aid(role,n) for n in ['C1','C2','C3']];ring=add('quinone_plane',plane,[aid(role,o) for o,c in available])
            if ring:
                center=np.array(ring['plane_center_A']);normal=np.array(ring['plane_normal'])
                for o,c in available:
                    offset=abs(float((lookup[aid(role,o)]-center)@normal))
                    if offset>.75:
                        candidates=[aid(role,n) for n in ['C1','C2','C3','C4','C5','C6','C7','C8','C9','C10'] if aid(role,n) in lookup and n!=c];third=max(candidates,key=lambda x:np.linalg.norm(np.cross(lookup[aid(role,o)]-lookup[aid(role,c)],lookup[x]-lookup[aid(role,c)])))
                        add(o+'_carbonyl_plane',[aid(role,c),aid(role,o),third],[aid(role,o)]);record['feature_notes'].append(f'{o} is {offset:.3f} Å outside the native C1/C2/C3 plane; an additional carbonyl section is shown.')
        assert record['slices'],sc['key'];scenes.append(record)
    with (N/'reports'/(pdb+'_atom_samples_v02.csv')).open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(samples[0]));w.writeheader();w.writerows(samples)
    result=dict(pdb=pdb,status='figures_generated',scientific_review='Not an automatic density-support approval. Prior human/visual flags remain in force.',source=info,scenes=scenes,atom_samples=len(samples));write(N/'reports'/(pdb+'_density_v02.json'),result)
    print(json.dumps(dict(pdb=pdb,scenes=len(scenes),sections=sum(len(s['slices']) for s in scenes),source=info)),flush=True);del grid,diff,native;gc.collect()
def main(ids,watch):
    atlas=js(R/'data/atlas.js');pending=[s for s in atlas['structures'] if not ids or s['pdb'] in ids]
    while pending:
        progressed=False
        for s in list(pending):
            pdb=s['pdb'];done=N/'reports'/(pdb+'_density_v02.json')
            if done.exists():pending.remove(s);continue
            try:source=load_source(pdb,ARGS);frame=bind_frame(pdb,ARGS)
            except (FileNotFoundError,json.JSONDecodeError):continue
            if source['state']=='source_error':
                write(done,dict(pdb=pdb,status='unavailable',message='No usable deposited map/structure-factor source could be retrieved from the checked official archives.',source_error=source.get('error'),scenes=[dict(scene=v['key'],protomer=p['number'],part=v['part'],slices=[],feature_notes=['Experimental density source unavailable.']) for p in s['protomers'] for v in p['views']]));pending.remove(s);progressed=True;continue
            if source['state']!='source_ready' or frame['status']!='PASS':continue
            try:prepare(s,source)
            except Exception as e:
                write(N/'reports'/(pdb+'_preparation_error_v02.json'),dict(pdb=pdb,error=repr(e)));raise
            pending.remove(s);progressed=True
        if not watch:break
        if pending and not progressed:time.sleep(5)
    print(json.dumps(dict(remaining=[s['pdb'] for s in pending])),flush=True)
    if pending:raise RuntimeError('Requested entries lack valid source/frame inputs')
if __name__=='__main__':main(ARGS.ids,ARGS.watch)
