"""Check rendered README/About coverage against canonical atlas and CSVs."""
from pathlib import Path
import argparse,csv,json,re
ROOT=Path(__file__).resolve().parents[1]
def js(p):return json.loads(p.read_text(encoding='utf-8').split('=',1)[1].strip().rstrip(';'))
def rows(p):
 with p.open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f))
def verify(R):
 A=js(R/'data/atlas.js');I=js(R/'data/density_interactive_index.js');c=A['counts'];counts={'Structures':len(A['structures']),'Deposited protomers':sum(len(s['protomers']) for s in A['structures']),'Scenes':sum(len(p['views']) for s in A['structures'] for p in s['protomers']),'Scene contact rows':len(rows(R/'downloads/all_contacts.csv')),'Unique atom pairs':len(rows(R/'downloads/tables/atlas_unique_contacts.csv')),'Numeric homologous comparison values':sum(bool(x['distance_A'].strip()) for x in rows(R/'downloads/compare_matrix.csv')),'Comparison cells, including blanks':len(rows(R/'downloads/compare_matrix.csv')),'Interactive density scenes':sum(x['status']=='available' for x in I['scenes'].values()),'Protomers with experimental-density figures':len({(x['pdb'],x['protomer']) for x in I['scenes'].values() if x['status']=='available'}),'Scenes with experimental-density figures':sum(x['status']=='available' for x in I['scenes'].values())}
 assert [counts[n] for n in ['Structures','Deposited protomers','Scenes','Scene contact rows','Unique atom pairs']]==[c[n] for n in ['structures','protomers','views','contacts','unique_contacts']]
 text=(R/'README.md').read_text(encoding='utf-8');table={m[0].strip():int(m[1].replace(',','')) for m in re.findall(r'^\| ([^|]+) \| ([\d,]+) \|$',text,re.M)}
 for k,v in counts.items():assert table.get(k)==v,(k,table.get(k),v)
 about=(R/'docs/GITHUB_ABOUT_PROPOSED.txt').read_text(encoding='utf-8').strip();assert len(about)<=350
 for token in [f"{c['structures']} PDB structures",f"{c['protomers']} protomers",f"{c['views']} scenes",f"{c['unique_contacts']} unique selected atom pairs",f"density for {counts['Protomers with experimental-density figures']} protomers"]:assert token in about,token
 assert about in (R/'docs/RELEASE_CANDIDATE.md').read_text(encoding='utf-8')
 assert 'A separate interactive-density pilot is under evaluation' not in text
 return dict(status='PASS',counts=counts,about_characters=len(about),scope='Canonical CSV/atlas coverage versus rendered README count table and proposed GitHub About text; selected rows/pairs are not confirmed hydrogen bonds. No remote description changed.')
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--repo',type=Path,default=ROOT);a.add_argument('--json',type=Path);v=a.parse_args();r=verify(v.repo)
 if v.json:v.json.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
 print(json.dumps(r,indent=2))
