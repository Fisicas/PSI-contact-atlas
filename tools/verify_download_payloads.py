"""Independently verify that file-preview download payloads preserve every original byte."""
from pathlib import Path
import argparse,hashlib,json
ROOT=Path(__file__).resolve().parents[1]
def verify(root=ROOT):
    keys=set();assets=total=0
    for file in sorted((root/'data/views').glob('*.js')):
        source=file.read_text(encoding='utf-8');scene=json.loads(source[source.rfind(']=')+2:].strip().rstrip(';'));key=scene['key'];keys.add(key)
        p=root/'data/downloads'/(key+'.js');lines=p.read_text(encoding='utf-8').splitlines();prefix='window.PSI_DOWNLOADS['+json.dumps(key)+']='
        assert len(lines)==2 and lines[1].startswith(prefix),(key,'payload assignment')
        payload=json.loads(lines[1][len(prefix):].rstrip(';'));assert payload['scene']==key and set(payload['assets'])=={'contacts','cif','pymol'}
        for kind,item in payload['assets'].items():
            rel=scene['downloads'][kind];path=(root/rel).resolve();assert path.is_relative_to(root.resolve())
            raw=path.read_bytes();assert item['source']==rel and item['filename']==path.name,(key,kind,'download identity')
            assert item['text'].encode('utf-8')==raw,(key,kind,'download content differs')
            assert item['sha256']==hashlib.sha256(raw).hexdigest(),(key,kind,'source hash')
            assert item['mime'].endswith(';charset=utf-8'),(key,kind,'encoding')
            assets+=1;total+=len(raw)
    assert keys and {p.stem for p in (root/'data/downloads').glob('*.js')}==keys
    return dict(status='PASS',scenes=len(keys),assets=assets,source_bytes=total,scope='Exact identities, UTF-8 round trips and source-byte hashes for CSV/mmCIF/PML download payloads. No coordinate/line-ending conversion.')
if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--json');v=a.parse_args();result=verify()
    if v.json:Path(v.json).write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))
