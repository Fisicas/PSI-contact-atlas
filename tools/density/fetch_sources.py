"""Fetch missing hash-bound map sources into a user-selected cache; never overwrite mismatches."""
import json,shutil,urllib.request
from pathlib import Path
from common import config,sha
a=config()
if not a.map_cache:raise ValueError('--map-cache is required')
for manifest in sorted((a.repo/'build/inputs/density_sources').glob('*.json')):
    s=json.loads(manifest.read_text(encoding='utf-8'))
    if a.ids and s['pdb'] not in a.ids:continue
    for r in s.get('records',[]):
        if not all(k in r for k in ['file','sha256','url']):continue
        rel=Path(r['file']);target=a.map_cache/rel
        if target.exists():assert sha(target)==r['sha256'];continue
        source=a.repo/'build/inputs/density_metadata'/rel.relative_to('raw_maps')
        target.parent.mkdir(parents=True,exist_ok=True)
        if source.is_file():shutil.copy2(source,target)
        else:
            part=target.with_suffix(target.suffix+'.part')
            if part.exists():raise FileExistsError(f'Preserved partial file exists: {part}')
            with urllib.request.urlopen(r['url'],timeout=90) as response,part.open('xb') as out:
                shutil.copyfileobj(response,out,4*1024*1024)
            assert sha(part)==r['sha256'],f'Source changed; preserved {part}; no silent replacement'
            part.rename(target)
        assert sha(target)==r['sha256']
        print(s['pdb'],rel,flush=True)
