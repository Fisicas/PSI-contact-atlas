"""Explicit path and source bindings shared by the density recipe."""
import argparse,gzip,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def config():
    a=argparse.ArgumentParser()
    a.add_argument('--repo',type=Path,default=ROOT)
    a.add_argument('--work-dir',type=Path,required=True)
    a.add_argument('--map-cache',type=Path)
    a.add_argument('--output-dir',type=Path)
    a.add_argument('--ids',nargs='*')
    a.add_argument('--contour-mode',choices=['primary','mean-plus-3sd'],default='primary')
    a.add_argument('--watch',action='store_true')
    v=a.parse_args();v.repo=v.repo.resolve();v.work_dir=v.work_dir.resolve()
    atlas=json.loads((v.repo/'data/atlas.js').read_text(encoding='utf-8').split('=',1)[1].strip().rstrip(';'))
    known={s['pdb'] for s in atlas['structures']}
    if v.ids and not set(v.ids)<=known:a.error('Unknown requested entry: '+', '.join(sorted(set(v.ids)-known)))
    v.output_dir=(v.output_dir or v.work_dir).resolve()
    v.map_cache=v.map_cache.resolve() if v.map_cache else None
    if v.repo==v.work_dir or v.repo in v.work_dir.parents:
        a.error('Keep the map/work cache outside the web repository')
    if v.contour_mode!='primary' and v.ids!=['9AU4']:
        a.error('The mean-plus-3SD display is explicitly limited to --ids 9AU4')
    (v.work_dir/'reports').mkdir(parents=True,exist_ok=True)
    (v.output_dir/'reports').mkdir(parents=True,exist_ok=True)
    return v
def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda:f.read(4*1024*1024),b''):h.update(chunk)
    return h.hexdigest()
def locate(rel,args):
    rel=str(rel).replace('\\','/')
    if rel.startswith('raw_maps/'):
        metadata=args.repo/'build/inputs/density_metadata'/Path(rel).relative_to('raw_maps')
        if metadata.is_file():return metadata
    if not args.map_cache:raise ValueError('A --map-cache is required for density preparation')
    path=args.map_cache/rel
    if path.is_file():return path
    index=args.map_cache/'cache_index.json'
    mapping=json.loads(index.read_text(encoding='utf-8')) if index.exists() else {}
    if rel in mapping and Path(mapping[rel]).is_file():return Path(mapping[rel])
    raise FileNotFoundError(f'Missing hash-bound source {rel}; use fetch_sources.py or a cache_index.json')
def source(cid,args):
    value=json.loads((args.repo/'build/inputs/density_sources'/f'{cid}.json').read_text(encoding='utf-8'))
    for record in value.get('records',[]):
        if record.get('file') and record.get('sha256'):
            path=locate(record['file'],args)
            assert sha(path)==record['sha256'],(cid,record['file'],'source SHA differs; never replace silently')
    def walk(o):
        if isinstance(o,dict):return {k:walk(v) for k,v in o.items()}
        if isinstance(o,list):return [walk(v) for v in o]
        if isinstance(o,str) and o.startswith('raw_maps/'):return str(locate(o,args))
        return o
    return walk(value)
def frame(cid,args):
    # This is a binding to the independently verified snapshot, not a new
    # live archive/model or map-quality claim.
    src=json.loads((args.repo/'build/config/sources.json').read_text(encoding='utf-8'))[cid]
    raw=gzip.decompress((args.repo/'build'/src['file']).read_bytes())
    assert hashlib.sha256(raw).hexdigest()==src['sha256']
    cfg=json.loads((args.repo/'build/config/scientific_review.json').read_text(encoding='utf-8'))
    row=next(r for r in cfg['current_snapshot_audit'] if r['pdb']==cid)
    assert row['archived_uncompressed_sha256']==src['sha256'] and row['status']=='IDENTICAL_ATOM_RECORDS'
    result=dict(pdb=cid,status='PASS',basis='Source-hash binding to independently checked archived/current snapshot; not a fresh live frame or map-quality test',review_date=cfg['date'],archived_source_sha256=src['sha256'])
    dest=args.work_dir/'reports'/f'{cid}_model_frame_v02.json'
    if not dest.exists():dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    return result
