"""Package exact UTF-8 scene-download bytes for file:// previews; no scientific conversion."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
MIME={'contacts':'text/csv;charset=utf-8','cif':'chemical/x-mmcif;charset=utf-8','pymol':'text/plain;charset=utf-8'}
def main():
    out=ROOT/'data/downloads';out.mkdir(exist_ok=True);count=total=0
    for file in sorted((ROOT/'data/views').glob('*.js')):
        text=file.read_text(encoding='utf-8');scene=json.loads(text[text.rfind(']=')+2:].strip().rstrip(';'));assets={}
        for kind in MIME:
            rel=scene['downloads'][kind];source=(ROOT/rel).resolve();assert source.is_relative_to(ROOT)
            raw=source.read_bytes();value=raw.decode('utf-8');assert value.encode('utf-8')==raw
            assets[kind]=dict(source=rel,filename=source.name,mime=MIME[kind],sha256=hashlib.sha256(raw).hexdigest(),text=value);total+=len(raw)
        data=dict(scene=scene['key'],assets=assets)
        payload='window.PSI_DOWNLOADS=window.PSI_DOWNLOADS||{};\nwindow.PSI_DOWNLOADS['+json.dumps(scene['key'])+']='+json.dumps(data,ensure_ascii=True,separators=(',',':'))+';\n'
        (out/(scene['key']+'.js')).write_text(payload,encoding='utf-8',newline='\n');count+=1
    print(f'Exact local-preview download payloads: {count} scenes, {count*3} files, {total} source bytes')
if __name__=='__main__':main()
