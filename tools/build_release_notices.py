"""Build concise release cautions and separately inspectable provenance facts."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
def main(root=ROOT):
    cfg=json.loads((root/'build/config/release_notices.json').read_text(encoding='utf-8'));structures=json.loads((root/'build/config/structures.json').read_text(encoding='utf-8'))
    assert set(cfg['entries'])=={s['pdb'] for s in structures}
    for s in structures:cfg['entries'][s['pdb']]['facts']=s.get('notes',[])
    (root/'data/release_notices.js').write_text('window.PSI_NOTICES = '+json.dumps(cfg,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf-8',newline='\n')
    print('Release notice policy:',len(cfg['entries']),'entries; specific cautions + provenance details')
if __name__=='__main__':main()
